from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum("patient", "doctor", "admin"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    appointments = relationship("Appointment", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    availability = relationship("Availability", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    time_slot = Column(String(50), nullable=False)

    doctor = relationship("Doctor", back_populates="availability")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    time_slot = Column(String(50), nullable=False)
    status = Column(Enum("booked", "completed", "cancelled"), default="booked")
    created_at = Column(TIMESTAMP, server_default=func.now())

    patient = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")