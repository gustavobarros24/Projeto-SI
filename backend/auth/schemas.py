import uuid

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    anamnesis_level: int
    anamnesis_xp: int
    radiology_level: int
    radiology_xp: int

    model_config = {"from_attributes": True}
