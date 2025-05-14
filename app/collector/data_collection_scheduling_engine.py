import app.collector.utils.constants_utils as constants

from app.collector.utils.api_client import (
    DatabaseProviderApiClient,
)
from datetime import datetime, timezone
import app.collector.utils.constants_utils as constants
from app.collector.utils.cron_utils import check_if_cron_is_today
from app.collector.utils.request_utils import (
    get_request,
    options_request,
    patch_request,
    post_request,
)
from app.schemas import (
    DatabaseProviderIngestionExecutionCreateSchema,
    DatabaseProviderIngestionLogCreateSchema,
    DatabaseProviderIngestionExecutionItemSchema,
)
import json
import uuid

from app.collector.data_collection_engine import DataCollectionEngine
from app.collector.utils.logging_config import setup_collector_logger
from app.models import SchedulingType


# Serialize UUID properties in json_body
def custom_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


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
                if  ("scheduling_type" in i) and \
                    ("scheduling" in i) and \
                    (i["scheduling_type"] == SchedulingType.CRON):
                    
                    cron_expression = i["scheduling"]
                # Check if the cron expression should be executed today.
                if cron_expression is not None and check_if_cron_is_today(
                    cron_expression
                ):
                    
                    logger, memory_stream = setup_collector_logger("app.collector")
                    logger.info(f"Processando DatabaseProviderIngestion {i['id']}")
                    provider_client = DatabaseProviderApiClient()
                    
                    ingestion = provider_client.get_ingestion(i["id"])
                    provider = provider_client.get(str(ingestion.provider_id))
                    connections = provider_client.get_connections(str(ingestion.provider_id))
                    
                    execution = DatabaseProviderIngestionExecutionCreateSchema(
                        status="preparing",
                        trigger_mode="manual",
                        triggered_by=None,  # FIXME
                        ingestion_id=ingestion.id,
                        created_at=datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
                    )
                    execution_json = json.loads(execution.model_dump_json())
                    execution_json.pop('logs')
                    post_return = post_request(constants.EXECUTION_ROUTE, execution_json)

                    execution = DatabaseProviderIngestionExecutionItemSchema(**post_return)
                    
                    status = "success"
                    try:
                        engine = DataCollectionEngine()
                        engine.execute_collection(provider, connections[0], ingestion)
                        logger.info(f"DatabaseProviderIngestion {i['id']} processado com sucesso.")
                    except Exception as e:
                        status = "error"
                        logger.error(f"Error {str(e)}", exc_info=True)
                        
                    
                    log_entry = DatabaseProviderIngestionLogCreateSchema(
                        execution_id=execution.id,
                        ingestion_id=ingestion.id,
                        #log=str(memory_stream.getvalue()),
                        log="teste",
                        status=status,
                    )
                    log_json = log_entry.model_dump()
                    
                    execution.status = status
                    execution_json = execution.model_dump()
                    execution_json["logs"] = [log_json]
                    
                    data=json.dumps(execution_json, default=custom_serializer)
                    print(data)
                    patch_request(constants.EXECUTION_ROUTE, str(execution.id), data)
                    
                    
                    
