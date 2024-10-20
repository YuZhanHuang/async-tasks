import time

from celery.utils.log import get_task_logger

from project.celery_utils import custom_celery_task
from project.database import db_context

logger = get_task_logger(__name__)


@custom_celery_task(bind=True)
def execute_task(self, task_id: str, payload: dict):
    current_task_id = self.request.id
    print(f"Task ID: {current_task_id}")

    time.sleep(3)

    # TODO 將狀態改為processing -> 需要commit
    # TODO 處理任務sleep 3 秒，再將任務改成 completed



