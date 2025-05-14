from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models
from .database import get_db
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
import uuid
import logging

router = APIRouter()

class PID(BaseModel):
    """
        PID == Person Identification Data/Information
        Contains personally identifying information from external source(s).
    """
    external_id: UUID
    name: str
    email: EmailStr
    date_of_birth: datetime

@router.post("/save", response_model=dict)
def save_person(person: PID, db: Session = Depends(get_db)):
    logging.info(f"Saving person: {person}")

    # Convert UUID to string for storage
    ext_id_str = str(person.external_id)

    # Check if person with this external_id already exists
    existing = db.query(models.Person).filter(models.Person.external_id == ext_id_str).first()
    if existing:
        detail = f"Person with external_id {ext_id_str} already exists in database"
        logging.warning(detail)
        return {"external_id": ext_id_str, "message": detail}

    db_person = models.Person(
        external_id=ext_id_str,
        name=person.name,
        email=person.email,
        date_of_birth=person.date_of_birth
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    detail = f"Person with external_id {ext_id_str} saved into database"
    logging.info(detail)
    return {"external_id": ext_id_str, "message": detail}

@router.get("/{external_id}", response_model=PID)
def get_person(external_id: str, db: Session = Depends(get_db)):
    logging.info(f"Fetching person with external_id: {external_id}")
    # Convert string ID to UUID to ensure proper type handling
    try:
        # Validate that the external_id is a valid UUID format
        uuid_obj = uuid.UUID(external_id)

        # Query using external_id as primary key
        person = db.query(models.Person).filter(models.Person.external_id == external_id).first()

        if person is None:
            detail = f"Person with external_id {external_id} not found in database"
            logging.error(detail)
            raise HTTPException(status_code=404, detail=detail)

        logging.info(f"Person fetched successfully: {external_id}")

        # Create UUID object from the stored string for the response
        external_id_uuid = uuid.UUID(person.external_id)

        return PID(
            external_id=external_id_uuid,
            name=person.name,
            email=person.email,
            date_of_birth=person.date_of_birth
        )
    except ValueError:
        detail = f"Invalid UUID format: {external_id}"
        logging.error(detail)
        raise HTTPException(status_code=400, detail=detail)
