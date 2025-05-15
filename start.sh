#!/bin/bash

export PGHOST='dbstore-gsi-des01.gsi.mpmg.mp.br'    
export PGPORT=60680
export PGUSER='postgres'
export PGDATABASE='limoeiro'
export PGPASSWORD='limoeiro%23GSI.MPMG'

/home/appuser/.venv/bin/pgq install
/home/appuser/.venv/bin/alembic downgrade -1
/home/appuser/.venv/bin/alembic upgrade head
exec /home/appuser/.venv/bin/uvicorn app.main:app --port 8080 --host 0.0.0.0
