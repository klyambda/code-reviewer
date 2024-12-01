from uuid import uuid4

from loguru import logger
from flask import request
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource
from flask import request, send_file

import config
from src.to_pdf import markdown_to_pdf
from services.evraz import EvrazManager
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

        
        if lang == "csharp":
            format_type = ".cs"
        elif lang == "ts":
            format_type = ".ts"
        else:
            return {"message": "bad lang"}
        project_manager = ProjectManager(format_type=format_type)
        project_manager.insert_project(file.filename.rstrip(".zip"))
        try:
            project_manager.extract_archive_and_save(file)
        except Exception as e:
            logger.exception(e)
            return {"message": "Error with archive"}, 400


        _project = col_projects.find_one({"_id": ObjectId(project_manager.project_id)})

        project_manager = ProjectManager(format_type=format_type)
        highlevel_content = project_manager.format_tree(_project.get("structure", {}))
        files = col_files.find({"project_id": _project["_id"]})
        logger.debug(highlevel_content)

        evraz_manager = EvrazManager()
        files_content = []
        for file in files:
            file_content = file.get("content")
            if file_content and file["name"].lower().endswith(format_type):
                files_content.append(
                    f'{highlevel_content}\n{file["name"]}\n{file_content}\n{_project.get("additional_settings_promt", "")}'
                )
        if lang == "csharp":
            answers = evraz_manager.generate_file_answer_csharp(files_content)
        elif lang == "ts":
            answers = evraz_manager.generate_file_answer_ts(files_content)

        file_pdf = f"{uuid4().hex[:7]}.pdf"
        markdown_to_pdf("\n".join(answers), file_pdf)
        return send_file(
            file_pdf,
            as_attachment=True,
            download_name=file_pdf,
            mimetype="application/pdf"
        )