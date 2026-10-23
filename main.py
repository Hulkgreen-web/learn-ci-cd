from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tente de créer les tables au démarrage si la base PostgreSQL est accessible
    try:
        models.Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print(
            f"Attention: Impossible de se connecter à la base de données au démarrage: {e}"
        )
    yield


app = FastAPI(title="Todo API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/tasks/",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une tâche",
)
def create_task(
    task: schemas.TaskCreate,
    db: Annotated[Session, Depends(get_db)],
):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get(
    "/tasks/",
    response_model=list[schemas.TaskResponse],
    summary="Lire les tâches",
)
def get_tasks(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    return db.query(models.Task).offset(skip).limit(limit).all()
