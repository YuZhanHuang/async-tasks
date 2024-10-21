import asyncio
import time

from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from project.async_tasks.models import Task
from project.celery_utils import custom_celery_task
from project.constants import TaskStatus
from project.database import db_context

logger = get_task_logger(__name__)


@custom_celery_task(bind=True)
def execute_task(self, task_id: str, *args, **kwargs):
    try:
        # celery 的 AsyncResult的id
        async_result_id = self.request.id

        # 將任務狀態改為進行中
        with db_context() as session:
            task = session.get(Task, task_id)
            task.async_result_id = async_result_id
            task.status = TaskStatus.processing.value
            session.commit()

        # 模擬複雜任務執行中
        time.sleep(3)

        # 修改並標記任務完成
        with db_context() as session:
            task = session.get(Task, task_id)
            task.status = TaskStatus.completed.value
            session.commit()
    except Exception as e:
        with db_context() as session:
            task = session.get(Task, task_id)
            if task:
                task.status = TaskStatus.failure.value
                task.error_message = str(e)
                session.commit()
        raise


async def execute_task_v2(task_id: int, db: AsyncSession):
    # 更新任務狀態為 "processing"
    async with db.begin():
        task = await db.get(Task, task_id)
        if task:
            task.status = TaskStatus.processing.value
            await db.commit()

    # 模擬任務執行
    await asyncio.sleep(30)

    # 更新任務狀態為 "completed"
    async with db.begin():
        task.status = TaskStatus.completed.value
        await db.commit()


async def cancel_task_v2(task_id: str, db: AsyncSession):
    # 查找並取消 pending 狀態的任務
    async with db.begin():
        task = await db.get(Task, task_id)
        if task and task.status in [TaskStatus.pending.value, TaskStatus.processing.value]:
            task.status = "cancelled"
            await db.commit()
            return True

    return False
