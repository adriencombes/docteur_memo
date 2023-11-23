##### BUILT-IN IMPORTS #####

import hashlib
import uuid

##### EXTERNAL IMPORTS #####

from fastapi import FastAPI, Request, Response
from sqlalchemy import select, exc


##### INTERNAL IMPORTS #####

from settings import session
from users import Caregiver, HealthPro, Patient, User


##### FUNCTIONS #####

def sqla_obj_todict(row):
    """Convert a database row (basically a class from Users package) in dict"""
    obj_as_dict = row.__dict__
    del obj_as_dict["_sa_instance_state"]
    return obj_as_dict


def fetch_user_by_name(name):
    """Given a name, return the associated User row from database"""
    statement = select(User).filter_by(name=name.capitalize())
    return session.execute(statement).fetchone()


def logged_healthpro(request):
    """Return True if the requester is a logged healthpro"""
    logged_name = SESSION_DB.get(request.cookies.get("Authorization"))
    if logged_name:
        role = sqla_obj_todict(fetch_user_by_name(logged_name)[0])["status"]
        return role == "healthpro"
    return False


def logged_neurologist(request):
    """Return True if the requester is a logged neurologist"""
    logged_name = SESSION_DB.get(request.cookies.get("Authorization"))
    if logged_healthpro(request):
        statement = select(HealthPro).filter_by(name=logged_name)
        user = sqla_obj_todict(session.execute(statement).fetchone()[0])
        return user["specialty"] == "neurologist"
    return False


##### INITIALIZATION #####

RANDOM_SESSION_ID = str(uuid.uuid4())
SESSION_DB = {}


##### DOC #####

DESCRIPTION = """
### Available endpoint *(unfold each to see params)*

*Each endpoint's params are required unless specified

<details>
 <summary><code>GET</code> <code><b>/login</b></code> - *(Authentify using your username and password)*</summary>

> | Parameters | Data type | description        |
> |------------|-----------|--------------------|
> | name       | string    | non-case sensitive |
> | password   | string    | case sensitive     |

</details>

<details>
 <summary><code>GET</code> <code><b>/status</b></code> - *(See database and authentification status)*</summary>

> No parameters

</details>

<details>
 <summary><code>POST</code> <code><b>/create_user/{name}</b></code> - *(Add a new user to the database)*</summary>

> | Parameters   | Data type | description                                                                         |
> |--------------|-----------|-------------------------------------------------------------------------------------|
> | name         | string    | non-case sensitive                                                                  |
> | status       | string    | can only be 'caregiver','healthpro' or 'patient'                                    |
> | password     | string    | case sensitive                                                                      |
> | age          | integer   | only for patient role                                                               |
> | mmse         | integer   | only for patient role / 0 <= mmse <= 30                                             |
> | caregiver_id | string    | only for patient role (optionnal)                                                   |
> | specialty    | string    | only for healthpro role / can only be 'general','psychologist' or 'neurologist'     |

</details>

<details>
 <summary><code>GET</code> <code><b>/get_user_by_name/{name}</b></code> - *(Search an user by name)*</summary>

> | Parameters   | Data type | description        |
> |--------------|-----------|--------------------|
> | name         | string    | non-case sensitive |

</details>

<details>
 <summary><code>GET</code> <code><b>/count_over/{mmse}</b></code> - *(Count users aged between to number, with mmse over a given number)*</summary>

> | Parameters   | Data type | description                                     |
> |--------------|-----------|-------------------------------------------------|
> | mmse         | int       | 0 <= mmse <= 30                                 |
> | min_age      | int       | Can be used with or without max_age (optionnal) |
> | max_age      | int       | Can be used with or without min_age (optionnal) |

</details>

<details>
 <summary><code>GET</code> <code><b>/count_under/{mmse}</b></code> - *(Count users aged between to number, with mmse under a given number)*</summary>

> | Parameters   | Data type | description                                     |
> |--------------|-----------|-------------------------------------------------|
> | mmse         | int       | 0 <= mmse <= 30                                 |
> | min_age      | int       | Can be used with or without max_age (optionnal) |
> | max_age      | int       | Can be used with or without min_age (optionnal) |

</details>

<details>
 <summary><code>GET</code> <code><b>/predict_patient/{name}</b></code> - *(Use our model to predict an user's mmse)*</summary>

> | Parameters   | Data type | description                                     |
> |--------------|-----------|-------------------------------------------------|
> | name         | string    | non-case sensitive                              |

</details>

"""


##### ENDPOINTS #####

app = FastAPI(title="Docteur Memo API", description=DESCRIPTION, version="1.0.0")


@app.get("/")
def root(request: Request):
    endpoints = {
        "To authentify using name/password [GET]": f"{request.url}login",
        "To see database and authentification status [GET]": f"{request.url}status",
        "To add an user to the database [POST]": f"{request.url}create_user/name",
        "To search user by name [GET]": f"{request.url}get_user_by_name/name",
        "To count users with mmse over [GET]": f"{request.url}count_over/0",
        "To count users with mmse under [GET]": f"{request.url}count_under/30",
        "To predict an user's mmse [GET]": f"{request.url}predict_patient/name",
    }

    return {
        "API_status": "Running",
        "API Documentation": f"{request.url}docs",
        "avalaible endpoints": endpoints,
    }


@app.get("/login")
async def login(response: Response, name: str, password: str):
    def check_password(user_dict, password):
        password = hashlib.md5(password.encode()).hexdigest()
        return user_dict["password"] == password

    user = fetch_user_by_name(name)
    try:
        user_dict = sqla_obj_todict(user[0])
        allow = check_password(user_dict, password)
        if not allow:
            return {"error": f"wrong password for user : {name}"}
        response.set_cookie(key="Authorization", value=RANDOM_SESSION_ID)
        SESSION_DB[RANDOM_SESSION_ID] = name.capitalize()
        return {"success": "you are logged in"}

    except TypeError:
        return {"error": f"user name not found : {name}"}


@app.get("/status")
def debug(request: Request):
    num_of_users = session.execute(select(User)).raw.rowcount
    num_of_patients = session.execute(select(Patient)).raw.rowcount
    num_of_healthpros = session.execute(select(HealthPro)).raw.rowcount
    num_of_caregivers = session.execute(select(Caregiver)).raw.rowcount
    name = SESSION_DB.get(request.cookies.get("Authorization"), None)
    role = sqla_obj_todict(fetch_user_by_name(name)[0])["status"] if name else None
    if role and logged_neurologist(request):
        role = "neurologist"

    return {
        "num of users in DB": num_of_users,
        "num of patients in DB": num_of_patients,
        "num of healthpros in DB": num_of_healthpros,
        "num of caregivers in DB": num_of_caregivers,
        "current user": name,
        "current role": role,
    }


@app.get("/create_user/{name}")
# @app.post("/create_user/{name}")
def create_user(
    response: Response,
    request: Request,
    name: str,
    status: str,
    password: str,
    age: int = None,
    mmse: int = None,
    caregiver_id: str = None,
    specialty: str = None,
):
    if fetch_user_by_name(name):
        response.status_code = 400
        return {"error": "this name is already taken. Please choose another one"}

    if status.lower() == "healthpro":
        if logged_healthpro(request):
            try:
                HealthPro(name, specialty).add(session, password)
                user = sqla_obj_todict(fetch_user_by_name(name)[0])
                user["password"] = len(password) * "*"

                response.status_code = 201
                return {"user_created": user}

            except exc.IntegrityError:
                session.rollback()
                response.status_code = 400
                return {
                    "error": "incorrect or missing parameters. pleaser refer to API's readme"
                }

        response.status_code = 403
        return {"error": "only authentified healthpros can create healthpro users"}

    elif status.lower() == "caregiver":
        Caregiver(name).add(session, password)
        user = sqla_obj_todict(fetch_user_by_name(name)[0])
        user["password"] = len(password) * "*"

        response.status_code = 201
        return {"user_created": user}

    elif status.lower() == "patient":
        try:
            Patient(name, age, mmse, caregiver_id).add(session, password)
            user = sqla_obj_todict(fetch_user_by_name(name)[0])
            user["password"] = len(password) * "*"

            response.status_code = 201
            return {"user_created": user}

        except exc.IntegrityError:
            session.rollback()
            response.status_code = 400
            return {
                "error": "incorrect or missing parameters. pleaser refer to API's readme"
            }
    else:
        response.status_code = 400
        return {
            "error": "invalid status specified : must be 'caregiver','healthpro' or 'patient'"
        }


@app.get("/get_user_by_name/{name}")
def get_user_by_name(response: Response, name: str):
    user = fetch_user_by_name(name)
    try:
        user = sqla_obj_todict(user[0])

        if user["status"] == "caregiver":
            statement = select(Caregiver).filter_by(name=user["name"])
            return session.execute(statement).fetchone()

        elif user["status"] == "healthpro":
            statement = select(HealthPro).filter_by(name=user["name"])
            return session.execute(statement).fetchone()

        elif user["status"] == "patient":
            statement = select(Patient).filter_by(name=user["name"])
            return session.execute(statement).fetchone()

    except TypeError:
        response.status_code = 404
        return {"error": f"user name not found : {name}"}


@app.get("/count_over/{mmse}")
def count_over(mmse: int, min_age: int = None, max_age: int = None):
    if min_age and max_age:
        statement = select(Patient).where(
            (Patient.mmse > mmse) & (Patient.age > min_age) & (Patient.age < max_age)
        )
    elif min_age:
        statement = select(Patient).where(
            (Patient.mmse > mmse) & (Patient.age > min_age)
        )
    elif max_age:
        statement = select(Patient).where(
            (Patient.mmse > mmse) & (Patient.age < max_age)
        )
    else:
        statement = select(Patient).where(Patient.mmse > mmse)
    return {"count": session.execute(statement).raw.rowcount}


@app.get("/count_under/{mmse}")
def count_under(mmse: int, min_age: int = None, max_age: int = None):
    if min_age and max_age:
        statement = select(Patient).where(
            (Patient.mmse < mmse) & (Patient.age > min_age) & (Patient.age < max_age)
        )
    elif min_age:
        statement = select(Patient).where(
            (Patient.mmse < mmse) & (Patient.age > min_age)
        )
    elif max_age:
        statement = select(Patient).where(
            (Patient.mmse < mmse) & (Patient.age < max_age)
        )
    else:
        statement = select(Patient).where(Patient.mmse < mmse)
    return {"count": session.execute(statement).raw.rowcount}


@app.get("/predict_patient/{name}")
def predict_patient(response: Response, request: Request, name: str):
    def fake_model(age):
        return 3 if age > 50 else 5

    name = name.capitalize()
    if not logged_neurologist(request):
        response.status_code = 403
        return {"error": "only authentified neurologist can make predictions"}

    if fetch_user_by_name(name):
        try:
            statement = select(Patient).filter_by(name=name)
            user = sqla_obj_todict(session.execute(statement).fetchone()[0])
            prediction = user["mmse"] + fake_model(user["age"])
            prediction = min(prediction, 30)
            return {"prediction": prediction}

        except TypeError:
            response.status_code = 404
            return {"error": f"patient not found : {name}"}

    response.status_code = 404
    return {"error": f"user name not found : {name}"}
