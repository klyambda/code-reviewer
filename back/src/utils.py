from json import JSONEncoder
from datetime import date, datetime


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date) or isinstance(obj, datetime):
                return obj.isoformat()
        except TypeError:
            pass
        return JSONEncoder.default(self, obj)
