import pytest

from project.async_tasks import async_task_router


async def create_task_helper(async_client):
    """Helper 函式：用來建立任務"""
    payload = {"task_name": "test_task"}
    response = await async_client.post(
        async_task_router.url_path_for("create_task"), json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "consumer processing"
    assert "task_id" in data
    return data["task_id"]


@pytest.mark.anyio
async def test_create_task(async_client):
    """測試建立任務 API"""
    task_id = await create_task_helper(async_client)
    assert task_id is not None


@pytest.mark.anyio
async def test_cancel_task(async_client):
    """測試取消任務 API"""
    # 使用 helper 函式建立任務
    task_id = await create_task_helper(async_client)

    # 取消該任務
    response = await async_client.post(
        async_task_router.url_path_for("cancel_task", task_id=task_id)
    )
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Task canceled"


@pytest.mark.anyio
async def test_task_status(async_client):
    """測試取消任務 API"""
    # 使用 helper 函式建立任務
    task_id = await create_task_helper(async_client)

    # 查詢該任務
    response = await async_client.get(
        async_task_router.url_path_for("get_async_task_status", task_id=task_id)
    )
    assert response.status_code == 200
    data = response.json()
    print('data', data)
    assert 'state' in data
