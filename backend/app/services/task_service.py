from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task
from app.repositories.tasks import create_task as repo_create_task
from app.repositories.tasks import set_task_failed as repo_set_task_failed
from app.services.queue import QueueClient


async def create_task(session: AsyncSession, payload: str) -> Task:
    return await repo_create_task(session=session, payload=payload)


async def enqueue_task(queue: QueueClient, task_id: UUID) -> None:
    await queue.publish_task(task_id)


async def mark_task_failed(session: AsyncSession, task: Task, result: str) -> None:
    await repo_set_task_failed(session=session, task=task, result=result)
