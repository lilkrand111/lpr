from fastapi import FastAPI, Path, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_session, engine, Base
from models import Note
from schemas import NoteCreate, NoteRead

app = FastAPI()

Base.metadata.create_all(bind=engine)


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
