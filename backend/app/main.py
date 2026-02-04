from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Task Queue API",
    description="Async task processing via RabbitMQ and PostgreSQL",
    lifespan=lifespan,
)

app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])


@app.get("/health")
async def health():
    return {"status": "ok"}
