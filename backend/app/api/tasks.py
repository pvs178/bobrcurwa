from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.task import TaskCreate, TaskCreated
from app.services.queue import QueueClient
from app.services.task_service import create_task, enqueue_task, mark_task_failed

router = APIRouter()


def get_queue(request: Request) -> QueueClient:
    queue = getattr(request.app.state, "queue", None)
    if queue is None:
        raise RuntimeError("Queue is not initialized")
    return queue


@router.post("", response_model=TaskCreated, status_code=status.HTTP_201_CREATED)
async def post_tasks(
    body: TaskCreate,
    session: AsyncSession = Depends(get_session),
    queue: QueueClient = Depends(get_queue),
) -> TaskCreated:
    task = await create_task(session=session, payload=body.payload)
    try:
        await enqueue_task(queue=queue, task_id=task.id)
    except Exception as e:
        await mark_task_failed(session=session, task=task, result=str(e))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Queue publish failed")
    return TaskCreated(task_id=task.id)
