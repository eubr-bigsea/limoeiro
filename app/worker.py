from __future__ import annotations
import asyncio
import json
import os

from fastapi import Request
from pgqueuer import Queries


import asyncpg

from pgqueuer import PgQueuer
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from app.collector import runner
from app.collector.utils.logging_config import setup_collector_logger
from app.models import DatabaseProviderIngestionLog
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def get_pgq_queries(request: Request) -> Queries:
    """Retrieve Queries instance from FastAPI app context."""
    return request.app.extra["pgq_queries"]


async def main() -> PgQueuer:
    connection = await asyncpg.connect(
        dsn=os.getenv("DB_URL", "").replace("+asyncpg", "")
    )
    driver = AsyncpgDriver(connection)
    pgq = PgQueuer(driver)

    # Entrypoint for jobs whose entrypoint is named 'fetch'.
    @pgq.entrypoint("start_ingestion")
    async def process_message(job: Job) -> None:
        if job.payload is not None:
            logger, memory_stream = setup_collector_logger("app.collector")
            payload = json.loads(job.payload.decode())
            logger.info(f"Processando mensagem: {job!r}: {payload}")

            db_url = os.getenv("DB_URL", "")
            engine = create_async_engine(db_url, echo=True)

            async_session = sessionmaker(
                bind=engine, # type: ignore
                class_=AsyncSession,
                expire_on_commit=False,
            )  # type: ignore

            status = "success"
            retries = 1
            for attempt in range(retries):
                try:
                    runner.execute(payload["execution"])
                    logger.info("Mensagem processada com sucesso.")
                    break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    #await asyncio.sleep(30)
                    if attempt == retries - 1:
                        logger.error(f"Error {str(e)}", exc_info=True)
                        status = "error"

            async with async_session() as session:  # type: ignore
                log_entry = DatabaseProviderIngestionLog(
                    execution_id=int(payload["execution"]),
                    ingestion_id=payload["ingestion"],
                    log=str(memory_stream.getvalue()),
                    status=status,
                )
                session.add(log_entry)
                await session.commit()
        # raise ValueError("Simulated error")

    return pgq
