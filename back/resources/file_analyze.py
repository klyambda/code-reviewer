from flask import request
from loguru import logger
from flask_restful import Resource, reqparse

from services.evraz import EvrazManager


class FileAnalyze(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("code", type=str)

    def post(self):
        """
        Анализ загруженного файла в формате .py или текста
        """
        file_content = None

        if "code" in request.files:
            file = request.files["code"]
            if not file.filename.lower().endswith(".py"):
                return {"message": "Only .py files are allowed"}, 400
            try:
                file_content = file.read().decode("utf-8")
            except Exception as e:
                return {"message": f"Error reading file: {str(e)}"}, 500

        if not file_content:
            data = FileAnalyze.parser.parse_args()
            if data.get("code") is None:
                return {"message": "No file or code provided"}, 400
            file_content = data["code"]

        evraz_manager = EvrazManager()
        try:
            answer = evraz_manager.generate_answer(file_content)
            return {"answer": answer}, 200
        except Exception as e:
            logger.exception(f"Ошибка {e} при запросе {file_content}")
            return {"message": "Evraz Chat API error"}, 500
