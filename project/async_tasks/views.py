import logging

from celery.result import AsyncResult
from fastapi import Request, Depends, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from project.async_tasks.models import Task
from project.async_tasks.schemas import task_schema
from project.async_tasks.tasks import execute_task, execute_task_v2, cancel_task_v2
from project.database import get_async_db_session
from project.async_tasks import async_task_router

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="project/async_tasks/templates")


@async_task_router.get("/form/")
async def form_example_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@async_task_router.post("/")
async def create_task(request: Request, session: AsyncSession = Depends(get_async_db_session)):
    payload = await request.json()
    payload = task_schema(payload)
    task = Task(task_name=payload['task_name'])
    async with session.begin():
        session.add(task)
        await session.commit()

    result = execute_task.delay(task.id)

    return {"message": "consumer processing", "task_id": result.id}


@async_task_router.get("/{task_id}/status/")
async def get_async_task_status(task_id):
    task = AsyncResult(task_id)
    state = task.state

    if state == 'FAILURE':
        error = str(task.result)
        response = {
            'state': state,
            'error': error,
        }
    else:
        response = {
            'state': state,
        }
    return response


@async_task_router.post("/{task_id}/cancel/")
async def cancel_task(task_id):
    result = AsyncResult(task_id)
    if result.state not in ['PENDING', 'STARTED']:
        return {"success": False, "message": "Task already completed or failed"}

    result.revoke(terminate=True)  # 終止任務
    result.backend.store_result(
        task_id,
        result={
            "exc_type": "TaskRevokedError",
            "exc_message": "Task was canceled"
        },
        state="REVOKED"
    )
    return {"success": True, "message": "Task canceled"}


# 以下為使用FastAPI原生的BackgroundTasks，寫出作為參考，異步任務還是會建議結合celery

@async_task_router.get("/v2/{task_id}")
async def get_task_status_v2(task_id: int, session: AsyncSession = Depends(get_async_db_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task.id, "status": task.status}


@async_task_router.post("/v2/")
async def create_task_v2(request: Request, background_tasks: BackgroundTasks,
                         session: AsyncSession = Depends(get_async_db_session)):
    payload = await request.json()
    new_task = Task(task_name=payload['task_name'])
    async with session.begin():
        session.add(new_task)
        await session.commit()

    background_tasks.add_task(execute_task_v2, new_task.id, session)

    return {"task_id": new_task.id, "status": new_task.status}


@async_task_router.post("/v2/{task_id}/cancel")
async def cancel_task(task_id: str, session: AsyncSession = Depends(get_async_db_session)):
    success = await cancel_task_v2(task_id, session)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"message": "Task cancelled", "task_id": task_id}
