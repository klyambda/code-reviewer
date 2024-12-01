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
    def post(self, project_id):
        project = col_projects.find_one({"_id": ObjectId(project_id)})
        if project is None:
            return {"message": f"No project with id {project_id}"}, 400

        project_manager = ProjectManager()
        highlevel_content = project_manager.format_tree(project.get("structure", {}))
        for folder, files in project_manager.files_by_folders.items():
            highlevel_content += "{}\n{}\n".format(folder, '\n'.join(files))

        print(highlevel_content)
        evraz_manager = EvrazManager()
        answer = evraz_manager.generate_structure_answer(highlevel_content)

        if answer == "EVRAZ_API_ERROR":
            return {"message": answer}, 500

        return {"answer": answer}, 200


class PipelineV2(Resource):
    def post(self, project_id):
        project = col_projects.find_one({"_id": ObjectId(project_id)})
        if project is None:
            return {"message": f"No project with id {project_id}"}, 400

        project_manager = ProjectManager()
        highlevel_content = project_manager.format_tree(project.get("structure", {}))
        files = col_files.find({"project_id": ObjectId(project_id)})

        evraz_manager = EvrazManager()
        files_content = []
        for file in files:
            file_content = file.get("content")
            if file_content and file["name"].lower().endswith(".py"):
                files_content.append(
                    f'{highlevel_content}\n{file["name"]}\n{file_content}\n{project.get("additional_settings_promt", "")}'
                )

        answers = evraz_manager.generate_files_answers(files_content)
        # TODO pdf
        return {"answer": answers}
