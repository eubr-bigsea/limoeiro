FROM python:3.11

RUN apt-get update && apt-get install -y libsasl2-dev
RUN apt-get install -y libsasl2-modules
RUN apt-get install libpq-dev
COPY . .
RUN pip install --upgrade pip && pip install -r ./requirements.txt

CMD alembic upgrade head && uvicorn app.main:app --reload --port 8080 --host 0.0.0.0