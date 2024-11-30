from loguru import logger
from flask import request
from flask_restful import Resource

import config
from services.project import ProjectManager


class Pipeline(Resource):
    def post(self):
        """Полный прогон через пайплайн проекта

        1. Загрузка проекта в формате .zip
        2. Распаковка файловой структуры и содержимого python файлов
        3. Анализ назначения каждого из файлов, находится ли он в нужной папке:
            3.1
        4. Подготовка отчета
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
        for folder, files in project_manager.files_by_folders.items():
            print(folder, "\n".join(files))

        return {"project_id": project_manager.project_id}, 200
