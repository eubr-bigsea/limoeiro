#!/bin/bash

/home/appuser/.venv/bin/alembic upgrade head
exec /home/appuser/.venv/bin/uvicorn app.main:app --port 8080 --host 0.0.0.0
