import os


ALLOWED_ARCHIVES_EXT = (".zip")
IGNORE_DIRS = (".git", )

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_BASE = os.getenv("MONGO_BASE")

EVRAZ_API_KEY = os.getenv("EVRAZ_API_KEY")


# Максимальное количество параллельных запросов в EVRAZ_API
max_parallel = 5
