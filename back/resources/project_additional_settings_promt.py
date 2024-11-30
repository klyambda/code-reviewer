from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

from src.mongo import col_projects
from services.task import task_manager
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectAdditionalSettingsPromt(Resource):
    def get(self, project_id):
        return {"message": "project is sent to Analyzer"}, 200

    def post(self, project_id):
        return {"message": "project is sent to Analyzer"}, 200
