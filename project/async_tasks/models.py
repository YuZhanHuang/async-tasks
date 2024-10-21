import uuid

from sqlalchemy import Column, String, Text, Boolean

from project.constants import TaskStatus
from project.database import Base


class Task(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, unique=True, default=lambda: str(uuid.uuid4()), index=True)
    task_name = Column(String, nullable=False)
    async_result_id = Column(String)
    status = Column(String, index=True, default=TaskStatus.pending.value)
    is_canceled = Column(Boolean, default=False)

