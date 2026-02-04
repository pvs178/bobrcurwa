from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.tasks import router as tasks_router
from app.db.session import init_db
from app.services.queue import QueueClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    queue = QueueClient()
    await queue.start()
    app.state.queue = queue
    yield
    await queue.stop()


app = FastAPI(
    title="Task Queue API",
    description="Async task processing via RabbitMQ and PostgreSQL",
    lifespan=lifespan,
)

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])


@app.get("/health")
async def health():
    return {"status": "ok"}
