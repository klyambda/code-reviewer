from loguru import logger
from flask import request
from flask_restful import Resource

import config
from services.project import ProjectManager
from src.mongo import col_projects, col_files


class Project(Resource):
    def get(self, project_id=None):
        if project_id:
            project = col_projects.find_one({"_id": project_id})
            if project is None:
                return {"message": f"No project with id {project_id}"}, 400

            files = col_files.find({"project_id": project_id}, {"project_id": 0, "created_at": 0})

            return {"structure": project.get("structure", {}), "files": files}, 200

        projects = []
        for project in col_projects.find({}, {"structure": 0}):
            projects.append(
                {
                    "_id": project["_id"],
                    "name": project["name"],
                    "created_at": project["created_at"],
                    "structure": project["structure"],
                }
            )
        return {"projects": projects}, 200

    def post(self, project_id=None):
        """
        Загрузка проекта в формате .zip с сохранением структуры и файлов .py
        """
        if "archive" not in request.files:
            return {"message": "No archive in the request"}, 400

        file = request.files["archive"]
        if not file.filename.lower().endswith(config.ALLOWED_ARCHIVES_EXT):
            return {"message": "Invalid archive file format, only .zip"}, 400

        project_manager = ProjectManager()
        project_id = project_manager.insert_project(file.filename)
        try:
            result = project_manager.extract_archive_and_return_result(file, project_id)
            result["project_id"] = project_id
        except Exception as e:
            logger.exception(e)
            return {"message": "Error with archive"}, 400

        return result, 200
