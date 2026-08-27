from fastapi import FastAPI
from sqlalchemy import text

from app.config import APP_NAME, APP_ENV
from app.database import Base, engine
from app.models.task import Task
from app.routers.task import router as task_router

from app.models import Task, User
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description="Production-style Task Management Backend",
    version="1.0.0",
)
app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
def root():
    return {
        "message": "Task Management API is running",
        "environment": APP_ENV,
    }


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected"
    }