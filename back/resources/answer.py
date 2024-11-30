from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

from src.mongo import col_projects, col_files


class ProjectAnswer(Resource):
    def get(self, project_id):
        try:
            project_id = ObjectId(project_id)
        except InvalidId:
            return {"message": f"No project with id {project_id}"}, 400

        project = col_projects.find_one({"_id": project_id}, {"answer": 1})
        if project is None:
            return {"message": f"No answer with id {project_id}"}, 400
        if "answer" not in project:
            return {"message": f"No answer yet for project with id {project_id}"}, 400

        return project["answer"], 200


class FileAnswer(Resource):
    def get(self, file_id):
        try:
            file_id = ObjectId(file_id)
        except InvalidId:
            return {"message": f"No file with id {file_id}"}, 400

        file = col_files.find_one({"_id": file_id}, {"answer": 1})
        if file is None or "answer" not in file:
            return {"message": f"No answer with id {file}"}, 400

        return file["answer"], 200
