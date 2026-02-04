import asyncio
import json
import random
from uuid import UUID

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage

from app.config import settings
from app.db.session import SessionLocal, init_db
from app.db.models import TaskStatus
from app.repositories.tasks import get_task, set_task_done, set_task_failed, set_task_processing


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        data = json.loads(message.body.decode("utf-8"))
        task_id = UUID(data["task_id"])

        async with SessionLocal() as session:
            task = await get_task(session=session, task_id=task_id)
            if task is None:
                return
            if task.status != TaskStatus.pending:
                return
            await set_task_processing(session=session, task=task)

            try:
                await asyncio.sleep(random.uniform(2, 5))
                result = f"Processed: {task.payload}"
                await set_task_done(session=session, task=task, result=result)
            except Exception as e:
                await set_task_failed(session=session, task=task, result=str(e))


async def run() -> None:
    await init_db()
    connection = await connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(settings.task_queue_name, durable=True)
    await queue.consume(handle_message)
    await asyncio.Future()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()

