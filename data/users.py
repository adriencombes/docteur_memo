
##### EXTERNAL IMPORTS #####

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

##### INTERNAL IMPORTS #####

Base = declarative_base()

##### CLASSES #####

class Patient(Base):
    __tablename__ = "patients"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    memory_score = Column(Integer)
    caregiver_id = Column(Integer)

    def __init__(self, name, age, memory_score, caregiver_id=None):
        self.name = name
        self.age = age
        self.memory_score = memory_score
        self.caregiver_id = caregiver_id

    def add(self, session):
        session.add(self)
        session.commit()


class Caregiver(Base):
    __tablename__ = "caregivers"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def add(self, session):
        session.add(self)
        session.commit()



class HealthPro(Base):
    __tablename__ = "healthpros"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)

    def __init__(self, name, specialty):
        self.name = name
        self.specialty = specialty

    def add(self, session):
        session.add(self)
        session.commit()
