from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str | None = None


class NoteRead(NoteCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
