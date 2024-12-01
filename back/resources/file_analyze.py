from loguru import logger
from flask import request
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

from services.task import task_manager
from services.evraz import EvrazManager
from src.mongo import col_files, col_projects


class FileAnalyze(Resource):
    def post(self, file_id=None):
        """
        Анализ загруженного файла в формате .py
        """
        evraz_manager = EvrazManager()
        file_content = None

        if "file" in request.files:
            file = request.files["file"]
            if not file.filename.lower().endswith(".py"):
                return {"message": "Only .py files are allowed"}, 400
            try:
                file_content = file.read().decode("utf-8")
                logger.debug(f"Start analyzing file {file.filename}")
                answer = evraz_manager.generate_file_answer(file_content)
                return {"answer": answer}, 200
            except Exception as e:
                return {"message": f"Error reading file: {str(e)}"}, 500

        elif file_id:
            file = col_files.find_one({"_id": file_id})
            if file is None:
                return {"message": f"No file with id {file_id}"}, 400

            project = col_projects.find_one({"_id": file["project_id"]})
            tree = project_manager.format_tree(project.get("structure", {}))
            if file.get("analyze"):
                # чтобы не делать, такой же анализ опять
                return {"message": "ok"}, 200
            col_files.update_one({"_id": file_id}, {"$set": {"analyze": True}})
            file_content = f"{tree}\n{file['name']}\n " + file["content"] + f'\n\n {project.get("additional_settings_promt", "")}'

        else:
            return {"message": "No file or file_id in the request"}, 400

        task_manager.create_task(
            "files",
            file_id,
            evraz_manager.generate_file_answer,
            file_content,
        )
        return {"message": "ok"}, 200
