from voluptuous import Schema, All, Required, REMOVE_EXTRA, Length, Email, In

from project.constants import TaskStatus


async_task_schema = Schema({
    Required("task_name"): All(str, Length(max=100)),  # 限制 task_name 長度
}, extra=REMOVE_EXTRA)
