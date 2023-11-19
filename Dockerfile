FROM python:3.8
WORKDIR /docteur_memo
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./docteur_memo .
CMD bash -c "python main.py" ; uvicorn api:app --host 0.0.0.0