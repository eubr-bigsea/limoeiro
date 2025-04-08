import json
import typing
import uuid
from app.collector.utils.constants_utils import (
    ASSET_ROUTE,
    CONNECTION_ROUTE,
    DATABASE_ROUTE,
    EXECUTION_ROUTE,
    INGESTION_ROUTE,
    PROVIDER_ROUTE,
    TABLE_ROUTE,
)
from app.collector.utils.request_utils import get_request, patch_request
from app.schemas import (
    DatabaseItemSchema,
    DatabaseListSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderIngestionExecutionItemSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseProviderItemSchema,
    DatabaseTableListSchema,
)


class AssetApiClient:
    @staticmethod
    def disable_many(ids: typing.List[typing.Union[str, uuid.UUID]]):
        status, info = patch_request(
            ASSET_ROUTE, path="disable-many", json_body=ids
        )
        return info


class DatabaseProviderApiClient:
    def get(self, provider_id: str):
        status, provider_info = get_request(PROVIDER_ROUTE, path=provider_id)
        return DatabaseProviderItemSchema(**provider_info)

    def get_ingestions(self, provider_id: str):
        status, ingestion_info = get_request(
            INGESTION_ROUTE, params={"provider_id": provider_id}
        )
        return [
            DatabaseProviderIngestionItemSchema(
                **{"provider_id": uuid.UUID(provider_id), **info}
            )
            for info in ingestion_info.get("items")
        ]

    def get_ingestion(self, ingestion_id: str):
        status, ingestion_info = get_request(INGESTION_ROUTE, path=ingestion_id)
        return DatabaseProviderIngestionItemSchema(**ingestion_info)

    def get_ingestion_execution(self, execution_id: str) -> DatabaseProviderIngestionExecutionItemSchema:
        status, execution_info = get_request(EXECUTION_ROUTE, path=execution_id)
        return DatabaseProviderIngestionExecutionItemSchema(**execution_info)

    def get_connections(self, provider_id: str):
        status, connection_info = get_request(
            CONNECTION_ROUTE, params={"provider_id": provider_id}
        )
        return [
            DatabaseProviderConnectionItemSchema(**info)
            for info in connection_info.get("items")
        ]


class DatabaseApiClient:
    def get(self, database_id: str):
        status, database_info = get_request(DATABASE_ROUTE, path=database_id)
        return DatabaseItemSchema(**database_info)

    def find_by_provider(self, provider_id: str):
        status, database_info = get_request(
            DATABASE_ROUTE, params={"provider_id": provider_id}
        )
        return [DatabaseListSchema(**info) for info in database_info["items"]]


class DatabaseTableApiClient:
    def find_by_database(self, database_id: str):
        status, database_info = get_request(
            TABLE_ROUTE, params={"database_id": database_id}
        )
        return [
            DatabaseTableListSchema(**info) for info in database_info["items"]
        ]
