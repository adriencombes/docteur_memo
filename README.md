# Senior Python Backend Developer Use-Case Proposal - *Adrien Combes*


## Project Overview

The goal of this use-case was to build both a database and an API to interrogate and modify this database.


## Contact Information

For any questions or additional information, please contact:

- **Email:** me@adriencombes.com
- **Phone:** +33 6 12 35 70 15


## Requirements

- **Docker** & **Docker compose**

- **Minikube**

- **Kubectl**

### **Python**

All this scripts are made to run inside a dedicated `python 3.8.10` environment. You'll find required librairies on `requirements.txt` - *Installation total size : 157,71MB (python excluded)*


<details>
 <summary>🐍 Pyenv users</summary>

  ```bash
  # from .
  pyenv install --skip-existing 3.8.10;
  pyenv virtualenv 3.8.10 UC-ACombes;
  pyenv local UC-ACombes;
  python3.8 -m pip install --upgrade pip;
  python3.8 -m pip install -r requirements.txt
  ```

  ```bash
  # to delete
  pyenv virtuaenv-delete UC-ACombes; rm .python-version
  ```
</details>

## Database

### Tables

I used **postgresql**, to build and host our database, made of 4 tables :

- **Users** *- That contains user_id, name, hashed password and status of each users*

> | user_id                          | name    | specialty | password                         |
> |----------------------------------|---------|-----------|----------------------------------|
> | a5434f31ca9e434ea829b73077db9abb | Adrien  | healthpro | 5f4dcc3b5aa123d61d8327deb882cf99 |
> | 38ac54f2b4de477cbf6dd697f9565ef9 | Adrien2 | patient   | 5f4dcc3b5aa123d61d8327deb882cf99 |

- **Healthpros** *- That contains user_id, name and specialty of each healthcare professionnals*

> | user_id                          | name    | specialty    |
> |----------------------------------|---------|--------------|
> | a5434f31ca9e434ea829b73077db9abb | Adrien  | neurologist  |
> | 38ac54f2b4de477cbf6dd697f9565ef9 | Adrien2 | psychologist |

- **Patients** *- That contains user_id, name, age, mmse and caregiver_id of each patients*

> | user_id                          | name    | age | mmse | caregiver_id                     |
> |----------------------------------|---------|-----|------|----------------------------------|
> | a5434f31ca9e434ea829b73077db9abb | Adrien  | 43  | 22   | 7f5135cd1024475da482a22a334c559d |
> | 38ac54f2b4de477cbf6dd697f9565ef9 | Adrien2 | 56  | 26   | 0a42426c7c2d40589c56e25486acc010 |

- **Caregivers** *- That contains user_id and name of each caregivers*

> | user_id                          | name    |
> |----------------------------------|---------|
> | a5434f31ca9e434ea829b73077db9abb | Adrien  |
> | 38ac54f2b4de477cbf6dd697f9565ef9 | Adrien2 |

### Procedural DB building

This use-case includes a script to fill the database with randomly generated data following this rules. *(Note that, no matter which solution you choose to deploy, this script will run if the database is found empty when initiated)* :

- A total of 10 000 users will be generated, distributed according to these proportions :

  - 60% of patients
  - 25% of caregivers
  - 7% of general_practitionner
  - 5% of psychologists
  - 3% of neurologists

- Each user will be associated with a random unique name and user_id

- A default password will set for all of them

- Patients age will be randomly choose between 25 and 90

- Patients mmse will be randomly choose between 5 and 30

- Patients will be fairly assigned to caregivers (caregiver_id could then be used as foreign key to link to caregivers table)


### API

This API is built on **fastapi** and **uvicorn**. *(Note that some endpoints, or actions will require the user to authentify first)*

**Here are available endpoint** *(unfold each to see params, all required unless specified)* :

<details>
 <summary><code>GET</code> <code><b>/docs</b></code> - *(Fastapi UI and present readme)*</summary>

> No parameters

</details>

<details>
 <summary><code>GET</code> <code><b>/login</b></code> - *(Authentify using your username and password)*</summary>

> | Parameters | Data type | description        |
> |------------|-----------|--------------------|
> | name       | string    | non-case sensitive |
> | password   | string    | case sensitive     |

> It will create a temporary cookie use to recognize user.

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

> Only authentified healthcare professionnals can create other healthpro users.

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

> Only neurologists will be able to use this endpoint. API will return an error to any other role or unauthentified user.

</details>



## Deployment

This use case can be deployed **multiple ways** :

### 1. Docker compose

To deploy directly on a machine, simply use
```
docker compose up
```

It will then fetch default postgresql image from docker, build the API image using given dockerfile, and configure both of them with `.dockerenv` file provided.

API will be accessible at http://localhost:2024

### 2. Docker compose for postgresql with local API

You could also want to use the postgresql in docker but run the API locally (to developp a new feature for example). Using
```
docker compose up
```
then
```
cd docteur-memo ; uvicorn api:app --reload
```

In this case you'll need to use direnv (or equivalent) to load environment variables from `.env`

API will then be accessible at http://localhost:8000 and every change on `docteur-memo/*.py` will reload and update the API.


### 3. Kubernetes in Minikube

First, start minikube and build image locally using
```
minikube start && minikube image build -t api .
```
Then build nodes using
```
cd deployment/minikube && kubectl apply -f .
```
Then check that pods are running using
```
kubectl get pods
```
As soon as they are, you'll be able to access API using url returned by
```
minikube service fastapi-service --url
```

### 4. Kubernetes in GKE

A complete version has been deployed to **Google Kubernetes Engine**, using deployment files in `deployment/k8s` and is available at http://104.155.111.43:2024/

<details>
 <summary>🛸 Easter eggs</summary>

- Will you find the 3 secret healthpro's specialties ?
- Will you guess the database password ? - *(hint : Capta1m Memo'5 5ubmar1me)*
- Will you find the map ?

</details>

### Misc

Note that DB and API could easilly be separated, for example to deploy the DB on VM and API.
Using docker compose you can also access the DB using localhost port 2025 to directly edit, or access it trough another service.

## Rebuild database

Note that at any point, you can reset the database, using procedural generation as detailed above. To do so, simply use docker exec, kubectl exec, or local terminal to run
```
python tables.py --rebuild
```


---


Thanks for reading.
