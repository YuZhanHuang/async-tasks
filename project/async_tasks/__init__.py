from fastapi import APIRouter

async_task_router = APIRouter(
    prefix="/async_tasks",
    tags=["Tasks"]
)

from . import models, tasks, views  # noqa