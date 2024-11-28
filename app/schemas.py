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



class DatabaseCreateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseUpdateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseItemSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseListSchema(BaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None
    domain: Optional["DomainListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(None)
    domain_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...

class DatabaseProviderCreateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderUpdateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderItemSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderListSchema(BaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    fully_qualified_name: Optional[str] = None
    display_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    domain: Optional["DomainListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_type_id: Optional[str] = Field(None)
    domain_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...

class DatabaseProviderTypeItemSchema(BaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[str] = None
    display_name: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderTypeListSchema(BaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[str] = None
    display_name: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaCreateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaUpdateSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaItemSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaListSchema(BaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    database: Optional["DatabaseListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseSchemaQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...

class DatabaseTableCreateSchema(BaseModel):
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
    columns: List['TableColumnCreateSchema']

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableUpdateSchema(BaseModel):
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
    columns: List['TableColumnUpdateSchema']

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableItemSchema(BaseModel):
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
    columns: List['TableColumnItemSchema']

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableListSchema(BaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = None
    display_name: Optional[str] = None
    fully_qualified_name: Optional[str] = None
    version: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseTableQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(None)
    database_schema_id: Optional[UUID] = Field(None)
    query: Optional[str] = Field(None)
    ...

class DomainCreateSchema(BaseModel):
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
    

class DomainUpdateSchema(BaseModel):
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
    

class DomainItemSchema(BaseModel):
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
    

class DomainListSchema(BaseModel):
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

class TableColumnCreateSchema(BaseModel):
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
    

class TableColumnUpdateSchema(BaseModel):
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
    

class TableColumnItemSchema(BaseModel):
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
    
