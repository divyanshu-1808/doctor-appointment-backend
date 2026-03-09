from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import engine
from auth import create_access_token, get_db
from utils import hash_password, verify_password

app = FastAPI()

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)


# -------------------------
# Root Test
# -------------------------

@app.get("/")
def root():
    return {"message": "Doctor Appointment Backend Running"}


# -------------------------
# Register API
# -------------------------

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------
# Login API
# -------------------------

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": db_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# -------------------------
# Doctors API
# -------------------------

@app.post("/doctors", response_model=schemas.DoctorResponse)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):

    new_doctor = models.Doctor(
        name=doctor.name,
        specialization=doctor.specialization
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor

from typing import Optional

@app.get("/doctors", response_model=list[schemas.DoctorResponse])
def get_doctors(specialization: Optional[str] = None,
                db: Session = Depends(get_db)):

    query = db.query(models.Doctor)

    if specialization:
        query = query.filter(models.Doctor.specialization == specialization)

    doctors = query.all()
    return doctors

@app.post("/appointments", response_model=schemas.AppointmentResponse)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db)
):

    # Check doctor availability
    slot = db.query(models.Availability).filter(
        models.Availability.doctor_id == appointment.doctor_id,
        models.Availability.date == appointment.date,
        models.Availability.time_slot == appointment.time_slot
    ).first()

    if not slot:
        raise HTTPException(
            status_code=400,
            detail="Doctor not available for this slot"
        )

    # Check if appointment already exists
    existing_appointment = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.date == appointment.date,
        models.Appointment.time_slot == appointment.time_slot,
        models.Appointment.status == "booked"
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="This slot is already booked"
        )

    new_appointment = models.Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        date=appointment.date,
        time_slot=appointment.time_slot,
        status="booked"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment



@app.post("/availability", response_model=schemas.AvailabilityResponse)
def create_availability(availability: schemas.AvailabilityCreate, db: Session = Depends(get_db)):

    existing_slot = db.query(models.Availability).filter(
        models.Availability.doctor_id == availability.doctor_id,
        models.Availability.date == availability.date,
        models.Availability.time_slot == availability.time_slot
    ).first()

    if existing_slot:
        raise HTTPException(
            status_code=400,
            detail="This availability slot already exists"
        )

    new_slot = models.Availability(
        doctor_id=availability.doctor_id,
        date=availability.date,
        time_slot=availability.time_slot
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot

@app.get("/availability/{doctor_id}", response_model=list[schemas.AvailabilityResponse])
def get_doctor_availability(doctor_id: int, db: Session = Depends(get_db)):

    slots = db.query(models.Availability).filter(
        models.Availability.doctor_id == doctor_id
    ).all()

    return slots

@app.get("/appointments/patient/{patient_id}", response_model=list[schemas.AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):

    appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).all()

    return appointments

@app.put("/appointments/cancel/{appointment_id}", response_model=schemas.AppointmentResponse)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):

    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    appointment.status = "cancelled"

    db.commit()
    db.refresh(appointment)

    return appointment



@app.get("/appointments/doctor/{doctor_id}", response_model=list[schemas.AppointmentResponse])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):

    appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id
    ).all()

    return appointments