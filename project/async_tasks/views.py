import logging

from celery.result import AsyncResult
from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from project.async_tasks.models import AsyncTask
from project.async_tasks.schemas import async_task_schema
from project.async_tasks.tasks import execute_task
from project.constants import TaskStatus
from project.database import get_db_session
from project.async_tasks import async_task_router

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="project/async_tasks/templates")


@async_task_router.get("/form/")
def form_example_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@async_task_router.post("/form/")
def create_async_tasks(payload: dict, session: Session = Depends(get_db_session)):
    # TODO 修正，請使用AsyncTask
    # FIXME 目前可以在內部拿到async_result id，可以自定義db資料對應celery_taskmeta
    async_result = execute_task.delay('fake_id', payload)
    print('async_result', async_result.id)

    return {"message": "consumer processing", "task_id": async_result.id}


@async_task_router.get("/{task_id}/status/")
def get_async_task_status(task_id):
    # TODO 修正，請使用AsyncTask
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
def cancel_task(task_id):
    result = AsyncResult(task_id)
    if result.state not in ['PENDING', 'STARTED']:
        return {"success": False, "message": "Task already completed or failed"}

    result.revoke(terminate=True)  # 終止任務
    result.backend.store_result(task_id, result="Task was canceled", state="REVOKED")
    return {"success": True, "message": "Task canceled"}


# 以上為集成celery的異步功能實現
# ------------------------------
# 以下為使用FastAPI的BackgroundTask，示範使用async與await執行，確保不blocking
# 此處就使用redis的部分
# from fastapi import FastAPI, BackgroundTasks
# import redis
# import uuid
# import json
#
# app = FastAPI()
#
# # 建立 Redis 連線
# redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
#
# STREAM_NAME = "my_stream"
#
# # Producer: 將消息加入 Redis Stream
# @app.post("/produce/")
# def produce_message(payload: dict):
#     message_id = str(uuid.uuid4())
#     redis_client.xadd(STREAM_NAME, {**payload, "message_id": message_id})
#     return {"message": "Message produced", "id": message_id}
#
# # Consumer: 使用 BackgroundTasks 來模擬即時消費
# @app.get("/consume/")
# def consume_messages(background_tasks: BackgroundTasks):
#     background_tasks.add_task(consume)
#     return {"message": "Consumer started"}
#
# def consume():
#     while True:
#         # 阻塞式讀取 Redis Stream 中的消息
#         messages = redis_client.xread({STREAM_NAME: "0"}, block=0)
#         for stream, entries in messages:
#             for entry_id, message in entries:
#                 print(f"Consumed message: {message}")
#                 # 處理完成後刪除該消息
#                 redis_client.xdel(STREAM_NAME, entry_id)
