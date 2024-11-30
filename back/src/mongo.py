import pymongo

import config


client = pymongo.MongoClient(
    f"mongodb://{config.MONGO_USERNAME}:{config.MONGO_PASSWORD}@{config.MONGO_HOST}:{config.MONGO_PORT}/"
)
db = client[config.MONGO_BASE]

col_projects = db["projects"]
col_files = db["files"]
col_answers = db["answers"]
