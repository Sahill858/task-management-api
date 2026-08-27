from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


def create_task(
    db: Session,
    task_data: TaskCreate,
    user_id: int,
) -> Task:
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        user_id=user_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_tasks(
    db: Session,
    skip: int,
    limit: int,
    status: str | None,
    priority: str | None,
    sort_by: str,
    order: str,
    user_id: int,
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)

    if status:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    allowed_sort_fields = {
        "id": Task.id,
        "title": Task.title,
        "created_at": Task.created_at,
    }

    sort_column = allowed_sort_fields.get(sort_by, Task.created_at)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    query = query.offset(skip).limit(limit)

    result = db.execute(query)

    return result.scalars().all()

def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)

def update_task(
    db: Session,
    task: Task,
    update_data: dict,
) -> Task:
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task

def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()