from io import StringIO

from loguru import logger
from flask_restful import Resource, reqparse
from flask import request, send_file
from bson import ObjectId
from bson.errors import InvalidId

import config
from src.mongo import col_projects, col_files
from services.evraz import EvrazManager
from services.project import ProjectManager


class PipelineV1(Resource):
    def post(self):
        if "file" not in request.files:
            return {"message": "No archive file in the request"}, 400

        file = request.files["file"]
        if not file.filename.lower().endswith(config.ALLOWED_ARCHIVES_EXT):
            return {"message": "Invalid archive file format, only .zip"}, 400

        project_manager = ProjectManager()
        project_manager.insert_project(file.filename.rstrip(".zip"))
        try:
            project_manager.extract_archive_and_save(file)
        except Exception as e:
            logger.exception(e)
            return {"message": "Error with archive"}, 400

        content = project_manager.format_tree(project_manager.structure)
        for folder, files in project_manager.files_by_folders.items():
            content += "{}\n{}\n".format(folder, '\n'.join(files))

        print(content)
        evraz_manager = EvrazManager()
        answer = evraz_manager.generate_structure_answer(content)

        if answer == "EVRAZ_API_ERROR":
            return {"message": answer}, 500

        return {"answer": answer}, 200


class PipelineV2(Resource):
    def post(self, project_id):
        try:
            project_id = ObjectId(project_id)
        except InvalidId:
            return {"message": f"No project with id {project_id}"}, 400

        project = col_projects.find_one({"_id": project_id})
        if project is None:
            return {"message": f"No project with id {project_id}"}, 400

        project_manager = ProjectManager()
        highlevel_content = project_manager.format_tree(project.get("structure", {}))
        files = col_files.find({"project_id": project_id},)

        files_content = []
        for file in files:
            file_content = file.get("content")
            if file_content:
                files_content.append(file_content)

        evraz_manager = EvrazManager()
        answers = evraz_manager.generate_files_answers(highlevel_content + file_content)

        if answer == "EVRAZ_API_ERROR":
            return {"message": answer}, 500

        return answer
        # memory_file = StringIO(content)
        # memory_file.seek(0)
        # return send_file(memory_file, as_attachment=True, mimetype='text/plain', download_name='report.md')
