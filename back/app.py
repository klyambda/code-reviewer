from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from resources.pipeline import PipelineV1, PipelineV2
from resources.answer import FileAnswer, ProjectAnswer
from resources.project import Project
from resources.file_analyze import FileAnalyze
from resources.project_analyze import ProjectAnalyze
from resources.project_additional_settings_promt import ProjectAdditionalSettingsPromt
from resources.chuck_code_analyze import ProjectChuckCodeAnalyze
from src.utils import CustomJSONEncoder


app = Flask(__name__)
app.config["RESTFUL_JSON"] = {"cls": CustomJSONEncoder}
CORS(app)

api = Api(app)
api.add_resource(PipelineV1, "/v1/pipeline")
api.add_resource(PipelineV2, "/v2/pipeline/<project_id>")
api.add_resource(FileAnswer, "/answers/files/<file_id>")
api.add_resource(ProjectAnswer, "/answers/projects/<project_id>")
api.add_resource(Project, "/projects", "/projects/<project_id>")
api.add_resource(ProjectAnalyze, "/analyze/projects/<project_id>")
api.add_resource(ProjectAdditionalSettingsPromt, "/additional_settings_promt/projects/<project_id>")
api.add_resource(ProjectChuckCodeAnalyze, "/analyze/chunk/files/<file_id>")
api.add_resource(FileAnalyze, "/analyze/files", "/analyze/files/<file_id>")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
