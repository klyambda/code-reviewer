from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource

from src.mongo import col_answers


class Answer(Resource):
    def get(self, answer_id):
        try:
            answer_id = ObjectId(answer_id)
        except InvalidId:
            return {"message": f"No file with id {answer_id}"}, 400

        answer = col_answers.find_one({"_id": answer_id})
        if answer is None:
            return {"message": f"No answer with id {answer}"}, 400

        return answer, 200
