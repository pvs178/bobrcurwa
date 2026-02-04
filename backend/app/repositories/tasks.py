from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task, TaskStatus


async def create_task(session: AsyncSession, payload: str) -> Task:
    task = Task(payload=payload, status=TaskStatus.pending)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: UUID) -> Task | None:
    return await session.scalar(select(Task).where(Task.id == task_id))


async def set_task_failed(session: AsyncSession, task: Task, result: str) -> None:
    task.status = TaskStatus.failed
    task.result = result
    await session.commit()


async def set_task_processing(session: AsyncSession, task: Task) -> None:
    task.status = TaskStatus.processing
    await session.commit()


async def set_task_done(session: AsyncSession, task: Task, result: str) -> None:
    task.status = TaskStatus.done
    task.result = result
    await session.commit()
