from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str


class NoteRead(NoteCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
