from datetime import datetime, timedelta

from loguru import logger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from src.mongo import col_files, col_projects


class TaskManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def create_task(self, entity_type, entity_id, func, *args):
        self.scheduler.add_job(
            self.execute_task,
            DateTrigger(datetime.now() + timedelta(seconds=1)),
            args=[entity_type, entity_id, func, *args],
        )

    def execute_task(self, entity_type, entity_id, func, *args):
        logger.debug(f"Starting task {entity_id}")
        result = func(*args)
        logger.debug(f"Task {entity_id} finished")

        data = {"$set": {"answer": result, "finished_at": datetime.now()}}
        if entity_type == "project":
            col_projects.update_one({"_id": entity_id}, data)
        elif entity_type == "files":
            col_files.update_one({"_id": entity_id}, data)


task_manager = TaskManager()
