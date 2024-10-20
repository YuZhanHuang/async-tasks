from fastapi import FastAPI

from project.celery_utils import create_celery


def create_app() -> FastAPI:
    app = FastAPI()

    from project.logging import configure_logging
    configure_logging()

    app.celery_app = create_celery()

    from project.async_tasks import async_task_router
    app.include_router(async_task_router)

    return app
