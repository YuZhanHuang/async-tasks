from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    canceled = "canceled"
    failure = "failure"


