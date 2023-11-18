
##### EXTERNAL IMPORTS #####

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

##### SETTINGS #####

host=os.environ.get('POSTGRES_SERVER')
port=os.environ.get('POSTGRES_PORT')
database=os.environ.get('POSTGRES_DB')
user=os.environ.get('POSTGRES_USER')
password=os.environ.get('POSTGRES_PASSWORD')
db_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'

##### INITIALIZATION #####

engine = create_engine(db_url,echo=False)
session = sessionmaker(bind=engine)()
meta = MetaData()
