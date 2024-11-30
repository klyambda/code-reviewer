from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource, reqparse

from src.mongo import col_projects, col_files
from services.task import task_manager
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectChuckCodeAnalyze(Resource):
    def get(self, file_id):
        data_file = col_files.find_one({"_id": file_id})
        if data_file:
            # TODO тут логика получить информацию

            # TODO для теста удалить
            from random import randint
            if randint(1, 10) == 2:
                # готово, вернуть результат (ключ не меняй)
                return {"result": "тут результ"}
            else:
                return {"result": "Ваш код анализируется, ожидайте"}, 200
        else:
            return {"message": "project not found"}, 404

    def post(self, file_id):
        parser = reqparse.RequestParser()
        parser.add_argument("code", type=str)
        data = parser.parse_args()
        print(data["code"])
        data_file = col_files.find_one({"_id": file_id})
        if data_file:
            # TODO тут логика создать задачу на промт для этого файла 

            project = col_projects.find_one({"_id": data_file["project_id"]})
            print(project.get("additional_settings_promt", ""))
            # ВАЖНО используя project.get("additional_settings_promt", "") (это доп промт от юзаре)
            return {"message": "ok"}, 200
        else:
            return {"message": "project not found"}, 404
