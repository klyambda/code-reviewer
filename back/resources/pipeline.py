from loguru import logger
from flask import request
from flask_restful import Resource

import config
from services.evraz import EvrazManager
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

        content = project_manager.format_tree(project_manager.structure)
        for folder, files in project_manager.files_by_folders.items():
            content += "{}\n{}".format(folder, '\n'.join(files))

        print(content)
        evraz_manager = EvrazManager()
        answer = evraz_manager.generate_structure_answer(content)

        return {"answer": answer}, 200
