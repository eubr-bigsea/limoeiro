import datetime
from uuid import UUID
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict

from .models import TableType
from .models import DataType
M = TypeVar('M')

class PaginatedSchema(BaseModel, Generic[M]):
    """ Used for pagination """
    page_size: int = Field(description="Page size")
    page_count: int = Field(description="Number of pages")
    page: int = Field(description="Page number")
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description=(
        "List of items items returned in the "
        "response following given criteria"))

    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseQuerySchema(BaseModel):
    """ Used for querying data """
    page: Optional[int] = Field(default=1, description="Page number")
    page_size: Optional[int] = Field(
        default=20,  description="Number of items per page")

    # Field selection
    include_fields: Optional[List[str]] = Field(
        None, description="Fields to include in the response")
    exclude_fields: Optional[List[str]] = Field(
        None, description="Fields to exclude from the response")

    sort_by: Optional[str] = Field(None, description="Sort option")
    sort_order: Optional[str] = Field(
        None, description="Sort ascending or descending",
        pattern="^(asc|desc)$")


class DatabaseBaseModel(BaseModel):
    ...

class DatabaseCreateSchema(DatabaseBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    fully_qualified_name: Optional[str] = None
    display_name: str
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: bool = False
    retention_period: Optional[str] = None

    # Associations
    provider_id: UUID
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseUpdateSchema(DatabaseBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: Optional[bool] = None
    retention_period: Optional[str] = None

    # Associations
    provider_id: Optional[UUID] = None
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseItemSchema(DatabaseBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: Optional[bool] = None
    retention_period: Optional[str] = None

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseListSchema(DatabaseBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(None)
    domain_id: Optional[UUID] = Field(None)
    layer_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    tags: Optional[str] = Field(None)
    ...
class DatabaseProviderBaseModel(BaseModel):
    ...

class DatabaseProviderCreateSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    fully_qualified_name: Optional[str] = None
    display_name: str
    description: Optional[str] = None
    version: str = "0.0.0"
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: bool = False
    configuration: Optional[str] = None

    # Associations
    provider_type_id: str
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderUpdateSchema(DatabaseProviderBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: Optional[bool] = None
    configuration: Optional[str] = None

    # Associations
    provider_type_id: Optional[str] = None
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderItemSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    owner: Optional[str] = None
    href: Optional[str] = None
    deleted: Optional[bool] = None
    configuration: Optional[str] = None

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderListSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_type_id: Optional[str] = Field(None)
    domain_id: Optional[UUID] = Field(None)
    layer_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...
class DatabaseProviderConnectionBaseModel(BaseModel):
    ...

class DatabaseProviderConnectionCreateSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for creating an instance"""
    user_name: str
    password: Optional[str] = None
    host: str
    port: int
    databases: Optional[str] = None
    all_database: bool = False
    schemas: Optional[str] = None
    tables: Optional[str] = None
    connection_scheme: Optional[str] = None
    extra_parameters: Optional[str] = None

    # Associations
    provider_id: UUID

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionUpdateSchema(DatabaseProviderConnectionBaseModel):
    """ Optional model for serialization of updating objects"""
    user_name: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    databases: Optional[str] = None
    all_database: Optional[bool] = None
    schemas: Optional[str] = None
    tables: Optional[str] = None
    connection_scheme: Optional[str] = None
    extra_parameters: Optional[str] = None

    # Associations
    provider_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionItemSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    databases: Optional[str] = None
    all_database: Optional[bool] = None
    schemas: Optional[str] = None
    tables: Optional[str] = None
    connection_scheme: Optional[str] = None
    extra_parameters: Optional[str] = None

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionListSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    user_name: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    databases: Optional[str] = None
    all_database: Optional[bool] = None
    schemas: Optional[str] = None
    tables: Optional[str] = None
    connection_scheme: Optional[str] = None
    extra_parameters: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderConnectionQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(None)
    ...
class DatabaseProviderIngestionBaseModel(BaseModel):
    ...

class DatabaseProviderIngestionCreateSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    deleted: bool = False
    type: str
    include_database: Optional[str] = None
    exclude_database: Optional[str] = None
    include_schema: Optional[str] = None
    exclude_schema: Optional[str] = None
    include_table: Optional[str] = None
    exclude_table: Optional[str] = None
    include_view: bool = False
    override_mode: Optional[str] = None
    scheduling: Optional[str] = None
    recent_runs_statuses: Optional[str] = None
    retries: int = 5

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionUpdateSchema(DatabaseProviderIngestionBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    deleted: Optional[bool] = None
    type: Optional[str] = None
    include_database: Optional[str] = None
    exclude_database: Optional[str] = None
    include_schema: Optional[str] = None
    exclude_schema: Optional[str] = None
    include_table: Optional[str] = None
    exclude_table: Optional[str] = None
    include_view: Optional[bool] = None
    override_mode: Optional[str] = None
    scheduling: Optional[str] = None
    recent_runs_statuses: Optional[str] = None
    retries: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionItemSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    deleted: Optional[bool] = None
    type: Optional[str] = None
    include_database: Optional[str] = None
    exclude_database: Optional[str] = None
    include_schema: Optional[str] = None
    exclude_schema: Optional[str] = None
    include_table: Optional[str] = None
    exclude_table: Optional[str] = None
    include_view: Optional[bool] = None
    override_mode: Optional[str] = None
    scheduling: Optional[str] = None
    recent_runs_statuses: Optional[str] = None
    retries: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionListSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    deleted: Optional[bool] = None
    type: Optional[str] = None
    include_database: Optional[str] = None
    exclude_database: Optional[str] = None
    include_schema: Optional[str] = None
    exclude_schema: Optional[str] = None
    include_table: Optional[str] = None
    exclude_table: Optional[str] = None
    include_view: Optional[bool] = None
    override_mode: Optional[str] = None
    scheduling: Optional[str] = None
    recent_runs_statuses: Optional[str] = None
    retries: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderIngestionQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(None)
    ...
class DatabaseProviderTypeBaseModel(BaseModel):
    ...

class DatabaseProviderTypeItemSchema(DatabaseProviderTypeBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[str] = None
    display_name: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderTypeListSchema(DatabaseProviderTypeBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[str] = None
    display_name: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseSchemaBaseModel(BaseModel):
    ...

class DatabaseSchemaCreateSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    display_name: str
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: str = "0.0.0"
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: bool = False

    # Associations
    database_id: UUID
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaUpdateSchema(DatabaseSchemaBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None

    # Associations
    database_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaItemSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None

    # Associations
    database: Optional["DatabaseListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaListSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    database: Optional["DatabaseListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseSchemaQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(None)
    layer_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...
class DatabaseTableBaseModel(BaseModel):
    ...

class DatabaseTableCreateSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for creating an instance"""
    type: TableType
    name: str
    display_name: str
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: str = "0.0.0"
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: bool = False
    proxy_enabled: bool = False
    query: Optional[str] = None
    cache_type: Optional[str] = None
    cache_ttl_in_seconds: Optional[int] = None
    cache_validation: Optional[str] = None

    # Associations
    database_id: UUID
    database_schema_id: UUID
    layer_id: Optional[UUID] = None
    columns: List['TableColumnCreateSchema']

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableUpdateSchema(DatabaseTableBaseModel):
    """ Optional model for serialization of updating objects"""
    type: Optional[TableType] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None
    proxy_enabled: Optional[bool] = None
    query: Optional[str] = None
    cache_type: Optional[str] = None
    cache_ttl_in_seconds: Optional[int] = None
    cache_validation: Optional[str] = None

    # Associations
    database_id: Optional[UUID] = None
    database_schema_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    columns: Optional[List["TableColumnUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableItemSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    type: Optional[TableType] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None
    proxy_enabled: Optional[bool] = None
    query: Optional[str] = None
    cache_type: Optional[str] = None
    cache_ttl_in_seconds: Optional[int] = None
    cache_validation: Optional[str] = None

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    columns: Optional[List["TableColumnItemSchema"]] = None
    tags: Optional[List["TagItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableListSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    tags: Optional[List["TagListSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseTableQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(None)
    database_schema_id: Optional[UUID] = Field(None)
    layer_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...
class DomainBaseModel(BaseModel):
    ...

class DomainCreateSchema(DomainBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    display_name: str
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: str = "0.0.0"
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DomainUpdateSchema(DomainBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DomainItemSchema(DomainBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DomainListSchema(DomainBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
class DomainQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(None)
    ...
class IAModelBaseModel(BaseModel):
    ...

class IAModelCreateSchema(IAModelBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    display_name: str
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: str = "0.0.0"
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: bool = False
    algorithm: Optional[str] = None
    tecnology: Optional[str] = None
    server: Optional[str] = None
    source: Optional[str] = None

    # Associations
    domain_id: Optional[UUID] = None
    attributes: Optional[List["IAModelAttributeCreateSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterCreateSchema"]] = None
    results: Optional[List["IAModelResultCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelUpdateSchema(IAModelBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None
    algorithm: Optional[str] = None
    tecnology: Optional[str] = None
    server: Optional[str] = None
    source: Optional[str] = None

    # Associations
    domain_id: Optional[UUID] = None
    attributes: Optional[List["IAModelAttributeUpdateSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterUpdateSchema"]] = None
    results: Optional[List["IAModelResultUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelItemSchema(IAModelBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None
    updated_by: Optional[str] = None
    href: Optional[str] = None
    owner: Optional[str] = None
    deleted: Optional[bool] = None
    algorithm: Optional[str] = None
    tecnology: Optional[str] = None
    server: Optional[str] = None
    source: Optional[str] = None

    # Associations
    domain: Optional["DomainListSchema"] = None
    attributes: Optional[List["IAModelAttributeItemSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterItemSchema"]] = None
    results: Optional[List["IAModelResultItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelListSchema(IAModelBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
class IAModelQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(None)
    ...
class IAModelAttributeBaseModel(BaseModel):
    ...

class IAModelAttributeCreateSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    description: Optional[str] = None
    deleted: bool = False
    usage: str = 'feature'

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeUpdateSchema(IAModelAttributeBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
    usage: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeItemSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
    usage: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeListSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
    usage: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class IAModelHyperParameterBaseModel(BaseModel):
    ...

class IAModelHyperParameterCreateSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    description: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterUpdateSchema(IAModelHyperParameterBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterItemSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterListSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class IAModelResultBaseModel(BaseModel):
    ...

class IAModelResultCreateSchema(IAModelResultBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    type: str
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultUpdateSchema(IAModelResultBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultItemSchema(IAModelResultBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultListSchema(IAModelResultBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class LayerBaseModel(BaseModel):
    ...

class LayerCreateSchema(LayerBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    display_name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class LayerUpdateSchema(LayerBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class LayerItemSchema(LayerBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class LayerListSchema(LayerBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class LayerQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(None)
    ...
class TableColumnBaseModel(BaseModel):
    ...

class TableColumnCreateSchema(TableColumnBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str
    display_name: str
    description: Optional[str] = None
    data_type: DataType
    array_data_type: Optional[str] = None
    size: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    position: Optional[int] = None
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False

    model_config = ConfigDict(from_attributes=True)
    

class TableColumnUpdateSchema(TableColumnBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[DataType] = None
    array_data_type: Optional[str] = None
    size: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    position: Optional[int] = None
    primary_key: Optional[bool] = None
    nullable: Optional[bool] = None
    unique: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
    

class TableColumnItemSchema(TableColumnBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[DataType] = None
    array_data_type: Optional[str] = None
    size: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    position: Optional[int] = None
    primary_key: Optional[bool] = None
    nullable: Optional[bool] = None
    unique: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
    
class TagBaseModel(BaseModel):
    ...

class TagItemSchema(TagBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    deleted: Optional[bool] = None
    description: Optional[str] = None
    applicable_to: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class TagListSchema(TagBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
