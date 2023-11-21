##### BUILT-IN IMPORTS #####

import uuid


##### EXTERNAL IMPORTS #####

import argparse
import hashlib
import numpy as np
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, inspect


##### INTERNAL IMPORTS #####

from settings import engine, meta


##### FUNCTIONS #####

def generate_id():
    return uuid.uuid4().hex


def init_tables_schemas(engine):
    users = Table(
        "users",
        meta,
        Column("user_id", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("password", String, nullable=False),
        Column("status", String, nullable=False),
    )

    patients = Table(
        "patients",
        meta,
        Column("user_id", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("age", Integer, nullable=False),
        Column("mmse", Integer, nullable=False),
        Column("caregiver_id", String, nullable=True),
    )

    caregivers = Table(
        "caregivers",
        meta,
        Column("user_id", String, primary_key=True),
        Column("name", String, nullable=False),
    )

    healthpros = Table(
        "healthpros",
        meta,
        Column("user_id", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("specialty", String, nullable=False),
    )

    meta.drop_all(engine)
    meta.create_all(engine)


def create_database(num_of_users, engine):
    print("Procedurally recreating database ...")

    def add_to_users_table(df, status):
        df = df[["user_id", "name"]].copy()
        df["status"] = status
        df["password"] = hashlib.md5("password".encode()).hexdigest()
        df.to_sql("users", engine, if_exists="append", index=False)

    init_tables_schemas(engine)

    generals = round(num_of_users * 0.07)
    psychologists = round(num_of_users * 0.05)
    neurologists = round(num_of_users * 0.03)
    caregivers = round(num_of_users * 0.25)
    healthpros = generals + psychologists + neurologists
    patients = num_of_users - healthpros - caregivers

    all_names = pd.read_csv("./names.csv")["name"].unique()
    all_names = np.random.choice(all_names, size=num_of_users)

    # healthpros

    names = all_names[:healthpros]
    names[0] = "Igor"
    ids = [generate_id() for n in range(len(names))]
    specialties = ["neurologist"] * neurologists + ["general"] * generals
    specialties += ["psychologist"] * psychologists

    df_healthpros = pd.DataFrame(
        list(zip(ids, names, specialties)), columns=["user_id", "name", "specialty"]
    )
    df_healthpros.to_sql("healthpros", engine, if_exists="append", index=False)
    add_to_users_table(df_healthpros, "healthpro")

    # caregivers

    n = healthpros
    names = all_names[n : n + caregivers]
    ids = [generate_id() for n in range(len(names))]

    df_caregivers = pd.DataFrame(list(zip(ids, names)), columns=["user_id", "name"])
    df_caregivers.to_sql("caregivers", engine, if_exists="append", index=False)
    add_to_users_table(df_caregivers, "caregiver")

    # patients

    n = healthpros + caregivers
    names = all_names[n : n + patients]
    ids = [generate_id() for n in range(len(names))]
    ages = np.random.randint(65, size=patients) + 25
    memory_score = np.random.randint(25, size=patients) + 5
    caregiver_ids = df_caregivers["user_id"].sample(n=patients, replace=True)
    caregiver_ids = caregiver_ids.reset_index(drop=True)

    df_patients = pd.DataFrame(
        list(zip(ids, names, ages, memory_score, caregiver_ids)),
        columns=["user_id", "name", "age", "mmse", "caregiver_id"],
    )
    df_patients.to_sql("patients", engine, if_exists="append", index=False)
    add_to_users_table(df_patients, "patient")

    print(f"Database recreated with {num_of_users} entries")
    print("Thanks for waiting. (See readme for creation details)")


def reset_tables(force_reset=False):
    tables_to_check = ["caregivers", "patients", "healthpros"]
    tables_present = inspect(engine).get_table_names()

    tables_missing = not all(value in tables_present for value in tables_to_check)

    if force_reset or tables_missing:
        create_database(10000, engine)
    else:
        print("\nDatabase found, rebuilt skipped\n")


##### LAUNCH #####

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", default=False)
    reset_tables(force_reset=parser.parse_args().rebuild)
