import app.collector.utils.constants_utils as constants
from app.collector.utils.cron_utils import check_if_cron_is_today
from app.collector.utils.request_utils import (
    get_request
)
from app.models import SchedulingType
from app.models import DatabaseProviderIngestionExecution
from pgqueuer import Queries
from app.database import get_session

class DataCollectionSchedulingEngine:
    """Class to implement the scheduling engine."""

    def __init__(self):
        pass

    def _get_ingestions(self, page):
        """Load the database provider ingestions."""
        dict_param = {"page": page, "page_size": 20}
        _, result = get_request(
            constants.INGESTION_ROUTE, None, params=dict_param
        )
        return result["items"], result["page"], result["page_count"]

    async def execute_engine(self, pgq_queries : Queries):
        """Execute the collection data engine."""
        current_page = 0
        page_count = None
        
        # Iter until last page.
        while current_page != page_count:
            """ Get all database providers with pagination. """
            current_page += 1
            ingestions, _, page_count = self._get_ingestions(current_page)

            # Iterate the database providers.
            for i in ingestions:
                cron_expression = None
                if  ("scheduling_type" in i) and \
                    ("scheduling" in i) and \
                    (i["scheduling_type"] == SchedulingType.CRON.value):
                    
                    cron_expression = i["scheduling"]

                # Check if the cron expression should be executed today.
                if cron_expression is not None and check_if_cron_is_today(
                    cron_expression
                ):
                    database_provider_ingestion_id = i['id']
                    
                    # Inicia uma ingestão de dados
                    execution = DatabaseProviderIngestionExecution(
                        status="preparing",
                        trigger_mode="manual",
                        triggered_by=None,  # FIXME
                        ingestion_id=database_provider_ingestion_id,
                    )
                    session = await get_session()
                    session.add(execution)
                    await session.flush()
                    job_ids = await pgq_queries.enqueue(
                        "start_ingestion",
                        payload=json.dumps(
                            {
                                "ingestion": str(database_provider_ingestion_id),
                                "execution": str(execution.id),
                            }
                        ).encode(),
                    )
                    execution.job_id = job_ids[0]
                    session.add(execution)
                    await session.commit()

                    
