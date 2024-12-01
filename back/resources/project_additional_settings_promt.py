from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource, reqparse

from src.mongo import col_projects
from services.task import task_manager
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectAdditionalSettingsPromt(Resource):
    def get(self, project_id):
        project = col_projects.find_one({"_id": ObjectId(project_id)})
        if project:
            return {"additional_settings_promt": project.get("additional_settings_promt", "")}
        else:
            return {"message": "project not found"}, 404

    def post(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument("additional_settings_promt", type=str)
        data = parser.parse_args()
        
        if col_projects.find_one({"_id": ObjectId(project_id)}):
            col_projects.update_one(
                {"_id": ObjectId(project_id)}, 
                {"$set": {"additional_settings_promt" : data["additional_settings_promt"]}}
            )
            return {"additional_settings_promt": data["additional_settings_promt"]}
        else:
            return {"message": "project not found"}, 404
        return {"message": "project is sent to Analyzer"}, 200
