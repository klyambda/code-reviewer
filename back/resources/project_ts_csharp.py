from loguru import logger
from flask import request
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

import config
from services.project import ProjectManager
from src.mongo import col_projects, col_files


class ProjectTsCshapr(Resource):
    def post(self, lang=None):
        """
        Загрузка проекта в формате .zip с сохранением структуры и файлов .py
        """
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

        structure_tree = project_manager.format_tree(project_manager.get("structure", {}))
        logger.debug(structure_tree)

        _project = col_projects.find({"_id": ObjectId(project_manager.project_id)})


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
        if lang = "csharp":
            answers = evraz_manager.generate_file_answer_csharp(files_content)
        elif lang = "ts":
            answers = evraz_manager.generate_file_answer_ts(files_content)

        file_pdf = f"{uuid4().hex[:7]}.pdf"
        markdown_to_pdf("\n".join(answers), file_pdf)
        return send_file(
            file_pdf,
            as_attachment=True,
            download_name=file_pdf,
            mimetype="application/pdf"
        )