from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import uuid

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"

    external_id = Column(String, primary_key=True, index=True) # We'd use a UUID here instead of String if we were committed to PGSQL or similar.
    name = Column(String)
    email = Column(String) # , index=True  might be worth exploring here

    date_of_birth = Column(DateTime)

    @validates("external_id")
    def validate_external_id(self, key, value):
        try:
            uuid.UUID(str(value))
        except ValueError:
            raise ValueError("external_id must be a valid UUID")
        return str(value)
