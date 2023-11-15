
##### EXTERNAL IMPORTS #####

import hashlib
import numpy as np
import pandas as pd
from sqlalchemy import Table, Column, Integer, String
import uuid

##### INTERNAL IMPORTS #####

from settings import meta

##### FUNCTIONS #####

def init_tables_schemas(engine):

    patients = Table(
        'patients', meta,
        Column('user_id', Integer, primary_key = True),
        Column('name', String),
        Column('age',Integer),
        Column('memory_score',Integer),
        Column('caregiver_id',Integer)
    )

    caregivers = Table(
        'caregivers', meta,
        Column('user_id', Integer, primary_key = True),
        Column('name', String)
    )

    healthpros = Table(
        'healthpros', meta,
        Column('user_id', Integer, primary_key = True),
        Column('name', String),
        Column('specialty',String)
    )

    meta.drop_all(engine)
    #meta.create_all(engine)

def create_database(num_of_users,engine):

    init_tables_schemas(engine)

    generals = round(num_of_users*0.07)
    psychologists = round(num_of_users*0.05)
    neurologists = round(num_of_users*0.03)
    caregivers = round(num_of_users*0.25)
    healthpros = generals+psychologists+neurologists
    patients = num_of_users - healthpros - caregivers

    all_names = pd.read_csv('data/names.csv')['name'].unique()
    all_names = np.random.choice(all_names, size=num_of_users)

    def generate_id():
        return uuid.uuid4().hex

    # healthpros

    names = all_names[:healthpros]
    ids = [generate_id() for n in range(len(names))]
    specialties = ['generals']*generals+['psychologists']*psychologists
    specialties += ['neurologists']*neurologists

    df_healthpros = pd.DataFrame(list(zip(ids, names, specialties)),
                columns =['user_id', 'name', 'speciality'])
    df_healthpros.to_sql('healthpros', engine, if_exists='replace', index=False)

    # caregivers

    n = healthpros
    names = all_names[n:n+caregivers]
    ids = [generate_id() for n in range(len(names))]

    df_caregivers = pd.DataFrame(list(zip(ids, names)),
                columns =['user_id', 'name'])
    df_caregivers.to_sql('caregivers', engine, if_exists='replace', index=False)

    # patients

    n = healthpros+caregivers
    names = all_names[n:n+patients]
    ids = [generate_id() for n in range(len(names))]
    ages = np.random.randint(65, size=patients)+25
    memory_score = np.random.randint(20, size=patients)+10
    caregiver_ids = df_caregivers['user_id'].sample(n=patients,replace=True)
    caregiver_ids = caregiver_ids.reset_index(drop=True)

    df_patients = pd.DataFrame(list(zip(ids, names, ages, memory_score, caregiver_ids)),
                columns =['user_id', 'name', 'age', 'mmse', 'caregiver_id'])
    df_patients.to_sql('patients', engine, if_exists='replace', index=False)

    pass
