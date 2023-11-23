FROM python:3.8
WORKDIR /docteur_memo
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./docteur-memo .
COPY ./.dockerenv .env
CMD bash -c "python tables.py" ; uvicorn api:app --host 0.0.0.0
