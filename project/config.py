import os
import pathlib
from functools import lru_cache

from kombu import Queue


def route_task(name, args, kwargs, options, task=None, **kw):
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "default"}


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
    ASYNC_DATABASE_URL: str = os.environ.get("ASYNC_DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
    DATABASE_CONNECT_DICT: dict = {}
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
    CELERY_TASK_DEFAULT_QUEUE: str = "default"

    # Force all queues to be explicitly listed in `CELERY_TASK_QUEUES` to help prevent typos
    CELERY_TASK_CREATE_MISSING_QUEUES: bool = False
    CELERY_TASK_QUEUES: list = (
        Queue("default"),
        Queue("high_priority"),
        Queue("low_priority"),
    )
    # All tasks with a name that matches project.users.tasks.* are routed to the high_priority queue.
    # Tasks that do not match that pattern will be routed to the default queue.
    CELERY_TASK_ROUTES = {
        "project.users.tasks.*": {
            "queue": "high_priority",
        },
    }
    # CELERY_TASK_ROUTES = (route_task,)
    """
    Celery workers send an acknowledgement back to the message broker after a task is picked up from the queue. 
    The broker will usually respond by removing the task from the queue. 
    This can cause problems if the worker dies while running the task and the task has been removed from the queue.

    To address this, you can configure the message broker to only acknowledge tasks 
    (and subsequently remove the task from the queue) after the tasks have completed (succeeded or failed).
    """
    CELERY_TASK_ACKS_LATE = True


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_CONNECT_DICT: dict = {"check_same_thread": False}


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
