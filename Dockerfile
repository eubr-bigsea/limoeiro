FROM python:3.11

RUN apt-get update && apt-get install -y libsasl2-dev
RUN apt-get install -y libsasl2-modules
RUN apt-get install libpq-dev
COPY . .
RUN pip install --upgrade pip && pip install uv && uv venv && uv sync
RUN apt-get install -V -y gettext
RUN msgfmt ./app/i18n/locales/en/LC_MESSAGES/messages.po -o ./app/i18n/locales/en/LC_MESSAGES/messages.mo
RUN msgfmt ./app/i18n/locales/pt/LC_MESSAGES/messages.po -o ./app/i18n/locales/pt/LC_MESSAGES/messages.mo

CMD .venv/bin/alembic upgrade head && .venv/bin/uvicorn app.main:app --reload --port 8080 --host 0.0.0.0
