import app.collector.utils.constants_utils as constants

from app.collector.utils.api_client import (
    DatabaseProviderApiClient,
)

import app.collector.utils.constants_utils as constants
from app.collector.utils.cron_utils import check_if_cron_is_today
from app.collector.utils.request_utils import (
    get_request,
    options_request,
    patch_request,
    post_request,
)
from app.models import DatabaseProviderIngestionExecution
from app.collector.data_collection_engine import DataCollectionEngine

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

    def execute_engine(self):
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
                if ("scheduling_type" in i) and ("scheduling" in i) and (i["scheduling_type"] == "cron"):
                    cron_expression = i["scheduling"]
                # Check if the cron expression should be executed today.
                if cron_expression is not None and check_if_cron_is_today(
                    cron_expression
                ):
                    provider_client = DatabaseProviderApiClient()
                    
                    ingestion = provider_client.get_ingestion(i["id"])
                    provider = provider_client.get(str(ingestion.provider_id))
                    connections = provider_client.get_connections(str(ingestion.provider_id))
                    
                    execution = DatabaseProviderIngestionExecution(
                        status="preparing",
                        trigger_mode="manual",
                        triggered_by=None,  # FIXME
                        ingestion_id=ingestion._id,
                    )
                    _, execution_post = post_request(constants.EXECUTION_ROUTE, execution.model_dump())

                    execution = DatabaseProviderIngestionExecution(**execution_post)
                    
                    status = "success"
                    try:
                        engine = DataCollectionEngine()
                        engine.execute_collection(provider, connections[0], ingestion)
                    except Exception as e:
                        status = "error"
                        
                    
                    execution.status = status
                    patch_request(
                        constants.EXECUTION_ROUTE, execution._id, execution.model_dump()
                    )
                    
