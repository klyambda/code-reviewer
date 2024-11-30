from flask_restful import Resource

from src.mongo import col_projects
from services.evraz import EvrazManager
from services.project import ProjectManager


class ProjectAnalyze(Resource):
    def post(self, project_id):
        """
        Анализ структуры загруженного проекта
        """
        project = col_projects.find_one({"_id": project_id})
        if project is None:
            return {"message": f"No project with id {project_id}"}, 400

        project_manager = ProjectManager()
        structure_tree = project_manager.format_tree(project.get("structure", {}))

        evraz_manager = EvrazManager()
        structure_answer = evraz_manager.generate_structure_answer(structure_tree)

        return {"answer": structure_answer}, 200
