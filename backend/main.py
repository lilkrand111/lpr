from fastapi import FastAPI, Path, HTTPException, Depends
from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from pathlib import Path as FilePath
from fastapi.staticfiles import StaticFiles

from .database import get_session, engine, Base
from .models import Note, User
from .schemas import (
    NoteCreate,
    NoteRead,
    UserCreate,
    UserOut,
    Token,
    TokenData,
)
from .security import get_password_hash

app = FastAPI()


@app.post("/notes", response_model=NoteRead, status_code=201)
def create_note(note_in: NoteCreate, session: Session = Depends(get_session)):
    note = Note(title=note_in.title, content=note_in.content)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


@app.get("/notes", response_model=list[NoteRead])
def get_notes(session: Session = Depends(get_session)):
    result = session.execute(select(Note))
    return result.scalars().all()


@app.get("/notes/{note_id}", response_model=NoteRead)
def get_note(
    note_id: Annotated[int, Path(ge=1)], session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    return note


@app.put("/notes/{note_id}", response_model=NoteRead)
def edit_note(
    note_id: Annotated[int, Path(ge=1)],
    note_in: NoteCreate,
    session: Session = Depends(get_session),
):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    note.title = note_in.title
    note.content = note_in.content
    session.commit()
    session.refresh(note)
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(
    note_id: Annotated[int, Path(ge=1)], session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    session.delete(note)
    session.commit()


@app.post("/register", status_code=201, response_model=UserOut)
def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует!"
        )
    session.refresh(user)
    return user


FRONTEND_DIR = FilePath(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
