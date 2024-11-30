from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource, reqparse

from src.mongo import col_projects, col_files
from services.task import task_manager
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectChuckCodeAnalyze(Resource):
    def post(self, file_id):
        parser = reqparse.RequestParser()
        parser.add_argument("code", type=str)
        data = parser.parse_args()
        data_file = col_files.find_one({"_id": file_id})
        if data_file:
            evraz_manager = EvrazManager()
            project = col_projects.find_one({"_id": data_file["project_id"]})

            answer = evraz_manager.generate_file_answer(
                data["code"] + f'\n\n {project.get("additional_settings_promt", "")}'
            )
            return {"message": "ok"}, 200
        else:
            return {"message": "file not found"}, 404
