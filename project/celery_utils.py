import functools
from datetime import datetime

from celery import current_app as current_celery_app, shared_task
from celery.signals import task_revoked
from celery.utils.time import get_exponential_backoff_interval
from sqlalchemy import MetaData, Table

from project.config import settings
from project.database import SessionLocal, engine


def create_celery():
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")

    return celery_app


class custom_celery_task:  # noqa

    EXCEPTION_BLOCK_LIST = (
        IndexError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    )

    def __init__(self, *args, **kwargs):
        self.task_args = args
        self.task_kwargs = kwargs

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self.EXCEPTION_BLOCK_LIST:
                # do not retry for those exceptions
                raise
            except Exception as e:
                # here we add Exponential Backoff just like Celery
                countdown = self._get_retry_countdown(task_func)
                raise task_func.retry(exc=e, countdown=countdown)

        task_func = shared_task(*self.task_args, **self.task_kwargs)(wrapper_func)
        return task_func

    def _get_retry_countdown(self, task_func):
        retry_backoff = int(
            max(1.0, float(self.task_kwargs.get('retry_backoff', True)))
        )
        retry_backoff_max = int(
            self.task_kwargs.get('retry_backoff_max', 600)
        )
        retry_jitter = self.task_kwargs.get(
            'retry_jitter', True
        )

        countdown = get_exponential_backoff_interval(
            factor=retry_backoff,
            retries=task_func.request.retries,
            maximum=retry_backoff_max,
            full_jitter=retry_jitter
        )

        return countdown


# 使用反射載入 celery_taskmeta 表
#
# @task_revoked.connect
# def on_task_revoked(request, terminated, signum, expired, **kwargs):
#     task_id = request.id
#
#     session = SessionLocal()
#     try:
#         # 查詢任務
#         task = session.query(celery_taskmeta).filter_by(task_id=task_id).first()
#
#         if task:
#             task.status = 'REVOKED'
#             task.date_done = datetime.utcnow()
#
#             # 提交變更
#             session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()




