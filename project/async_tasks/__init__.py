from fastapi import APIRouter

async_task_router = APIRouter(
    prefix="/async_tasks"
)

from . import models, tasks, views  # noqa