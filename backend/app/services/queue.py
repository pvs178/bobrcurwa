import json
import uuid

from aio_pika import DeliveryMode, Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from app.config import settings


class QueueClient:
    def __init__(self) -> None:
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queue: AbstractQueue | None = None

    async def start(self) -> None:
        self._connection = await connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(settings.task_queue_name, durable=True)

    async def stop(self) -> None:
        if self._channel is not None:
            await self._channel.close()
        if self._connection is not None:
            await self._connection.close()

        self._queue = None
        self._channel = None
        self._connection = None

    async def publish_task(self, task_id: uuid.UUID) -> None:
        if self._channel is None:
            raise RuntimeError("QueueClient is not started")
        body = json.dumps({"task_id": str(task_id)}).encode("utf-8")
        msg = Message(body=body, delivery_mode=DeliveryMode.PERSISTENT, content_type="application/json")
        await self._channel.default_exchange.publish(msg, routing_key=settings.task_queue_name)
