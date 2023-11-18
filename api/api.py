
##### EXTERNAL IMPORTS #####

from fastapi import FastAPI, Request
from sqlalchemy import select, union_all

##### INTERNAL IMPORTS #####

from api.settings import session
from api.users import Caregiver, HealthPro, Patient, User

##### FUNCTIONS #####

def sqla_obj_todict(sqlalchemy):
    obj_as_dict = sqlalchemy.__dict__
    del obj_as_dict['_sa_instance_state']
    return obj_as_dict

##### ENDPOINTS #####

description = """
Docteur Memo API
"""

app = FastAPI(title="Docteur Memo API",
              description=description,
              version="1.0.0")

@app.get("/")
def root(request : Request):
    return {'API_status':'Running'}


@app.get("/debug")
def debug(request : Request):

    #statement = union_all(
    #    select(Caregiver),
    #    select(HealthPro),
    #    select(Patient))
    statement = select(User)
    rows = session.execute(statement).all()
    return  rows


@app.get("/get_user_by_id")
def get_user(request : Request, user_id):
    statement = select(User).filter_by(user_id=user_id)
    user = session.execute(statement).fetchone()

    try:
        user = sqla_obj_todict(user[0])

        if user['status'] == "caregiver":
            statement = select(Caregiver).filter_by(user_id=user_id)
            return session.execute(statement).fetchone()

        elif user['status'] == "healthpro":
            statement = select(HealthPro).filter_by(user_id=user_id)
            return session.execute(statement).fetchone()

        elif user['status'] == "patient":
            statement = select(Patient).filter_by(user_id=user_id)
            return session.execute(statement).fetchone()

    except TypeError:
        return {'error':f'user not found : {user_id}'}


@app.get("/get_user_by_name")
def get_user(request : Request, name):
    name = name.capitalize()
    statement = select(User).filter_by(name=name)
    user = session.execute(statement).fetchone()

    try:
        user = sqla_obj_todict(user[0])

        if user['status'] == "caregiver":
            statement = select(Caregiver).filter_by(name=name)
            return session.execute(statement).fetchone()

        elif user['status'] == "healthpro":
            statement = select(HealthPro).filter_by(name=name)
            return session.execute(statement).fetchone()

        elif user['status'] == "patient":
            statement = select(Patient).filter_by(name=name)
            return session.execute(statement).fetchone()

    except TypeError:
        return {'error':f'user name not found : {name}'}


@app.get("/create_user")
#@app.post("/create_user")
def create_user(request : Request, name, status, password):

    name = name.capitalize()
    statement = select(User).filter_by(name=name)
    if session.execute(statement).fetchone():
        return {'error':f'user name "{name}" is already taken. Please choose another'}

    if status.lower() == "healthpro":
        return {'error':'only admins can create healthpro users'}

    elif status == "caregiver":
        Caregiver(name).add(session,password)
        statement = select(User).filter_by(name=name)
        user = sqla_obj_todict(session.execute(statement).fetchone()[0])
        user["password"] = len(password)*'*'
        return {"user_created":user}


#/create_user ( PUT )
#username
#password
