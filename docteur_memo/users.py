##### EXTERNAL IMPORTS #####

import hashlib
import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


##### INITIALIZATION #####

Base = declarative_base()


##### FUNCTIONS #####

def generate_id():
    return uuid.uuid4().hex


##### CLASSES #####

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    status = Column(String)

    def __init__(self, user_id, name, password, status):
        self.user_id = user_id
        self.name = name.capitalize()
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.status = status

    def add(self, session):
        session.add(self, session)
        session.commit()


class Caregiver(Base):
    __tablename__ = "caregivers"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.user_id = generate_id()
        self.name = name.capitalize()

    def add(self, session, password):
        session.add(self, session)
        session.commit()
        User(
            user_id=self.user_id, name=self.name, password=password, status="caregiver"
        ).add(session)


class HealthPro(Base):
    __tablename__ = "healthpros"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)

    def __init__(self, name, specialty):
        self.user_id = generate_id()
        self.name = name.capitalize()
        if specialty in ["general", "psychologist", "neurologist"]:
            self.specialty = specialty
        else:
            self.specialty = None

    def add(self, session, password):
        session.add(self, session)
        session.commit()
        User(
            user_id=self.user_id, name=self.name, password=password, status="healthpro"
        ).add(session)


class Patient(Base):
    __tablename__ = "patients"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    mmse = Column(Integer)
    caregiver_id = Column(Integer)

    def __init__(self, name, age, mmse, caregiver_id=None):
        self.user_id = generate_id()
        self.name = name.capitalize()
        self.age = age
        if not 1 <= int(mmse) <= 30:
            self.mmse = None
        else:
            self.mmse = mmse
        self.caregiver_id = caregiver_id

    def add(self, session, password):
        session.add(self, session)
        session.commit()
        User(
            user_id=self.user_id, name=self.name, password=password, status="patient"
        ).add(session)
