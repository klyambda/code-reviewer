from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

from src.mongo import col_projects
from services.task import task_manager
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectAnalyze(Resource):
    def post(self, project_id):
        """
        Анализ структуры загруженного проекта
        """
        try:
            project_id = ObjectId(project_id)
        except InvalidId:
            return {"message": f"No project with id {project_id}"}, 400

        project = col_projects.find_one({"_id": project_id})
        if project is None:
            return {"message": f"No project with id {project_id}"}, 400

        project_manager = ProjectManager()
        structure_tree = project_manager.format_tree(project.get("structure", {}))
        logger.debug(structure_tree)

        evraz_manager = EvrazManager()
        task_manager.create_task(
            "project",
            project_id,
            evraz_manager.generate_structure_answer,
            structure_tree,
        )
        return {"message": "project is sent to Analyzer"}, 200
