from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


# -------------------------
# User Schemas
# -------------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# Token Schema
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------
# Doctor Schema
# -------------------------

class DoctorCreate(BaseModel):
    name: str
    specialization: str


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    doctor_id: int
    date: date
    time_slot: str

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date: date
    time_slot: str
    status: str

    class Config:
        from_attributes = True
