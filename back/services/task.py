from time import time
from datetime import datetime

from loguru import logger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from src.mongo import col_answers


class TaskManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def create_task_and_return_answer_id(self, func, entity_type, entity_id, *args):
        data = {"started_at": datetime.now(), "status": "PENDING"}
        if entity_type == "project":
            data["project_id"] = entity_id
        elif entity_type == "file":
            data["file_id"] = entity_id
        answer_id = col_answers.insert_one(data).inserted_id

        self.scheduler.add_job(self.execute_task, DateTrigger(time() + 1), args=[answer_id, func, *args])

        return answer_id

    def execute_task(self, answer_id, func, *args):
        logger.debug(f"Starting task {answer_id}")
        result = func(*args)
        logger.debug(f"Task {answer_id} finished")
        col_answers.update_one(
            {"_id": answer_id},
            {"$set": {"answer": result, "status": "COMPLETED"}}
        )


task_manager = TaskManager()
