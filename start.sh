#!/bin/bash
set -e  # optional: fail fast on errors

/home/appuser/.venv/bin/pgq install
/home/appuser/.venv/bin/alembic upgrade head

# Start both in background
/home/appuser/.venv/bin/uvicorn app.main:app --port 8080 --host 0.0.0.0 &
UVICORN_PID=$!

/home/appuser/.venv/bin/python worker.py &
WORKER_PID=$!

# Wait for either to exit
wait $WORKER_PID $UVICORN_PID
