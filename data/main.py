
##### INTERNAL IMPORTS #####

from settings import engine
from tables import create_database
from sqlalchemy.engine.reflection import Inspector

##### TABLES CREATION #####

inspector = Inspector.from_engine(engine)
tables_to_check = ["caregivers", 'patients', 'healthpros']
tables_present = inspector.get_table_names()

if not all(value in tables_present for value in tables_to_check):
    create_database(1000000,engine)

create_database(1000000,engine)
