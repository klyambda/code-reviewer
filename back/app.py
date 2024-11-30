from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from resources.project import Project
from resources.file_analyze import FileAnalyze
from resources.project_analyze import ProjectAnalyze
from src.utils import CustomJSONEncoder


app = Flask(__name__)
app.config["RESTFUL_JSON"] = {"cls": CustomJSONEncoder}
CORS(app)

api = Api(app)
api.add_resource(Project, "/projects", "/projects/<project_id>")
api.add_resource(ProjectAnalyze, "/analyze/projects", "/analyze/projects/<project_id>")
api.add_resource(FileAnalyze, "/analyze/files",)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
