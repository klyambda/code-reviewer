from loguru import logger
from flask import request
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

import config
from services.project import ProjectManager
from src.mongo import col_projects, col_files


class Project(Resource):
    def get(self, project_id=None):
        if project_id:
            try:
                project_id = ObjectId(project_id)
            except InvalidId:
                return {"message": f"No project with id {project_id}"}, 400

            project = col_projects.find_one({"_id": project_id})
            if project is None:
                return {"message": f"No project with id {project_id}"}, 400

            files = col_files.find({"project_id": project_id}, {"project_id": 0, "created_at": 0})

            return {"structure": project.get("structure", {}), "files": list(files)}, 200

        return {"projects": list(col_projects.find({}, {"structure": 0}))}, 200

    def post(self, project_id=None):
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

        return {"project_id": project_manager.project_id}, 200
