from json import JSONEncoder
from datetime import date, datetime

from bson import ObjectId


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date) or isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return str(obj)
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)
