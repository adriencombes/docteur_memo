
##### EXTERNAL IMPORTS #####

from sqlalchemy import inspect

##### INTERNAL IMPORTS #####

from settings import engine
from tables import create_database

##### TABLES CHECK #####

def reset_tables(force_reset=False):
    tables_to_check = ["caregivers", 'patients', 'healthpros']
    tables_present = inspect(engine).get_table_names()

    tables_missing = not all(value in tables_present for value in tables_to_check)

    if force_reset or tables_missing:
        create_database(10000,engine)
    else:
        print("Database found")

##### LAUNCH #####

if __name__ == "__main__":
    reset_tables(force_reset=False)
