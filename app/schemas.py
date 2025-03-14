import datetime
from uuid import UUID
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

from .models import TableType
from .models import DataType
M = TypeVar('M')

class PaginatedSchema(BaseModel, Generic[M]):
    """ Used for pagination """
    page_size: int = Field(description="Tamanho da página")
    page_count: int = Field(description="Total de páginas")
    page: int = Field(description="Número da página")
    count: int = Field(description="Número de itens retornados na resposta")
    items: List[M] = Field(description=(
        "Lista de itens retornados"))

    model_config = ConfigDict(arbitrary_types_allowed=True)

class BaseQuerySchema(BaseModel):
    """ Used for querying data """
    page: Optional[int] = Field(Query(1, description="Número da página"))
    page_size: Optional[int] = Field(Query(
        default=20,  description="Número de itens por página"))

    # Field selection
    include_fields: Optional[str] = Field(Query(
        None, description="Campos a serem incluídos na resposa"))
    exclude_fields: Optional[str] = Field(Query(
        None, description="Campos a serem excluídos da resposta"))

    sort_by: Optional[str] = Field(Query(None, description="Opção de ordenação"))
    sort_order: Optional[str] = Field(Query(
        None, description="Ordenação ascendente ou descendente",
        pattern="^(asc|desc)$"))


class DatabaseBaseModel(BaseModel):
    ...

class DatabaseCreateSchema(DatabaseBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    retention_period: Optional[str] = Field(None, description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.")

    # Associations
    provider_id: UUID
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseUpdateSchema(DatabaseBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    retention_period: Optional[str] = Field(None, description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.")

    # Associations
    provider_id: Optional[UUID] = None
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseItemSchema(DatabaseBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    retention_period: Optional[str] = Field(None, description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.")

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseListSchema(DatabaseBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(Query(None, description="Provider"))
    domain_id: Optional[UUID] = Field(Query(None, description="Domínio"))
    layer_id: Optional[UUID] = Field(Query(None, description="Camada"))
    query: Optional[str] = Field(Query(None, description="Consulta"))
    tags: Optional[str] = Field(Query(None, description="Tags"))
    ...
class DatabaseProviderBaseModel(BaseModel):
    ...

class DatabaseProviderCreateSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: str = Field("0.0.0", description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    configuration: Optional[str] = Field(None, description="Configuração")

    # Associations
    provider_type_id: str
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderUpdateSchema(DatabaseProviderBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    configuration: Optional[str] = Field(None, description="Configuração")

    # Associations
    provider_type_id: Optional[str] = None
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderItemSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    configuration: Optional[str] = Field(None, description="Configuração")

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderListSchema(DatabaseProviderBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_type_id: Optional[str] = Field(Query(None, description="Provider type"))
    domain_id: Optional[UUID] = Field(Query(None, description="Domain"))
    layer_id: Optional[UUID] = Field(Query(None, description="Layer"))
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class DatabaseProviderConnectionBaseModel(BaseModel):
    ...

class DatabaseProviderConnectionCreateSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for creating an instance"""
    user_name: str = Field(..., description="Nome do usuário / login")
    password: Optional[str] = Field(None, description="Senha do usuário")
    host: str = Field(..., description="Nome do servidor")
    port: int = Field(..., description="Porta do servidor")
    database: Optional[str] = Field(None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(None, description="Parâmetros extras")

    # Associations
    provider_id: UUID

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionUpdateSchema(DatabaseProviderConnectionBaseModel):
    """ Optional model for serialization of updating objects"""
    user_name: Optional[str] = Field(None, description="Nome do usuário / login")
    password: Optional[str] = Field(None, description="Senha do usuário")
    host: Optional[str] = Field(None, description="Nome do servidor")
    port: Optional[int] = Field(None, description="Porta do servidor")
    database: Optional[str] = Field(None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(None, description="Parâmetros extras")

    # Associations
    provider_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionItemSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    user_name: Optional[str] = Field(None, description="Nome do usuário / login")
    password: Optional[str] = Field(None, description="Senha do usuário")
    host: Optional[str] = Field(None, description="Nome do servidor")
    port: Optional[int] = Field(None, description="Porta do servidor")
    database: Optional[str] = Field(None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(None, description="Parâmetros extras")

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderConnectionListSchema(DatabaseProviderConnectionBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    user_name: Optional[str] = Field(None, description="Nome do usuário / login")
    password: Optional[str] = Field(None, description="Senha do usuário")
    host: Optional[str] = Field(None, description="Nome do servidor")
    port: Optional[int] = Field(None, description="Porta do servidor")
    database: Optional[str] = Field(None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(None, description="Parâmetros extras")

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderConnectionQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(Query(None, description="Provider"))
    ...
class DatabaseProviderIngestionBaseModel(BaseModel):
    ...

class DatabaseProviderIngestionCreateSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    type: str = Field(..., description="Tipo de ingestão")
    include_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem incluídas na ingestão")
    exclude_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem excluídas da ingestão")
    include_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem incluídos na ingestão")
    exclude_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem excluídos da ingestão")
    include_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem incluídas na ingestão")
    exclude_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem excluídas da ingestão")
    include_view: bool = Field(False, description="Considerar views na ingestão")
    override_mode: Optional[str] = Field(None, description="Opção para sobrescrita")
    scheduling: Optional[str] = Field(None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(None, description="Status das últimas execuções")
    retries: int = Field(5, description="Max retries")

    # Associations
    provider_id: UUID

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionUpdateSchema(DatabaseProviderIngestionBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    type: Optional[str] = Field(None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem incluídas na ingestão")
    exclude_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem excluídas da ingestão")
    include_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem incluídos na ingestão")
    exclude_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem excluídos da ingestão")
    include_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem incluídas na ingestão")
    exclude_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem excluídas da ingestão")
    include_view: Optional[bool] = Field(None, description="Considerar views na ingestão")
    override_mode: Optional[str] = Field(None, description="Opção para sobrescrita")
    scheduling: Optional[str] = Field(None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(None, description="Status das últimas execuções")
    retries: Optional[int] = Field(None, description="Max retries")

    # Associations
    provider_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionItemSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    type: Optional[str] = Field(None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem incluídas na ingestão")
    exclude_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem excluídas da ingestão")
    include_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem incluídos na ingestão")
    exclude_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem excluídos da ingestão")
    include_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem incluídas na ingestão")
    exclude_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem excluídas da ingestão")
    include_view: Optional[bool] = Field(None, description="Considerar views na ingestão")
    override_mode: Optional[str] = Field(None, description="Opção para sobrescrita")
    scheduling: Optional[str] = Field(None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(None, description="Status das últimas execuções")
    retries: Optional[int] = Field(None, description="Max retries")

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderIngestionListSchema(DatabaseProviderIngestionBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    type: Optional[str] = Field(None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem incluídas na ingestão")
    exclude_database: Optional[str] = Field(None, description="Expressão regular para as bases a serem excluídas da ingestão")
    include_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem incluídos na ingestão")
    exclude_schema: Optional[str] = Field(None, description="Expressão regular para os esquemas a serem excluídos da ingestão")
    include_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem incluídas na ingestão")
    exclude_table: Optional[str] = Field(None, description="Expressão regular para as tabelas a serem excluídas da ingestão")
    include_view: Optional[bool] = Field(None, description="Considerar views na ingestão")
    override_mode: Optional[str] = Field(None, description="Opção para sobrescrita")
    scheduling: Optional[str] = Field(None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(None, description="Status das últimas execuções")
    retries: Optional[int] = Field(None, description="Max retries")

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseProviderIngestionQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    provider_id: Optional[str] = Field(Query(None, description="Provider"))
    ...
class DatabaseProviderTypeBaseModel(BaseModel):
    ...

class DatabaseProviderTypeItemSchema(DatabaseProviderTypeBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[str] = None
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    image: Optional[str] = Field(None, description="Imagem do tipo de provedor")

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseProviderTypeListSchema(DatabaseProviderTypeBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[str] = None
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    image: Optional[str] = Field(None, description="Imagem do tipo de provedor")

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseSchemaBaseModel(BaseModel):
    ...

class DatabaseSchemaCreateSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: str = Field("0.0.0", description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    # Associations
    database_id: UUID
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaUpdateSchema(DatabaseSchemaBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    # Associations
    database_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaItemSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    # Associations
    database: Optional["DatabaseListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseSchemaListSchema(DatabaseSchemaBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")

    # Associations
    database: Optional["DatabaseListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseSchemaQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(Query(None, description="Database"))
    layer_id: Optional[UUID] = Field(Query(None, description="Camada"))
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class DatabaseTableBaseModel(BaseModel):
    ...

class DatabaseTableCreateSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for creating an instance"""
    type: TableType = Field(..., description="Tipo da tabela")
    name: str = Field(..., description="Nome da instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: str = Field("0.0.0", description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    proxy_enabled: bool = Field(False, description="Indica se a tabela está disponível no proxy.")
    query: Optional[str] = Field(None, description="Consulta para gerar os dados, se for uma VIEW.")
    cache_type: Optional[str] = Field(None, description="Tipo de cache para a tabela.")
    cache_ttl_in_seconds: Optional[int] = Field(None, description="Tempo de validade do cache da tabela.")
    cache_validation: Optional[str] = Field(None, description="Comando para validar o cache")

    # Associations
    database_id: UUID
    database_schema_id: UUID
    layer_id: Optional[UUID] = None
    columns: List['TableColumnCreateSchema']

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableUpdateSchema(DatabaseTableBaseModel):
    """ Optional model for serialization of updating objects"""
    type: Optional[TableType] = Field(None, description="Tipo da tabela")
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    proxy_enabled: Optional[bool] = Field(None, description="Indica se a tabela está disponível no proxy.")
    query: Optional[str] = Field(None, description="Consulta para gerar os dados, se for uma VIEW.")
    cache_type: Optional[str] = Field(None, description="Tipo de cache para a tabela.")
    cache_ttl_in_seconds: Optional[int] = Field(None, description="Tempo de validade do cache da tabela.")
    cache_validation: Optional[str] = Field(None, description="Comando para validar o cache")

    # Associations
    database_id: Optional[UUID] = None
    database_schema_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    columns: Optional[List["TableColumnUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableItemSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    type: Optional[TableType] = Field(None, description="Tipo da tabela")
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    proxy_enabled: Optional[bool] = Field(None, description="Indica se a tabela está disponível no proxy.")
    query: Optional[str] = Field(None, description="Consulta para gerar os dados, se for uma VIEW.")
    cache_type: Optional[str] = Field(None, description="Tipo de cache para a tabela.")
    cache_ttl_in_seconds: Optional[int] = Field(None, description="Tempo de validade do cache da tabela.")
    cache_validation: Optional[str] = Field(None, description="Comando para validar o cache")

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    columns: Optional[List["TableColumnItemSchema"]] = None
    tags: Optional[List["TagItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class DatabaseTableListSchema(DatabaseTableBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    tags: Optional[List["TagListSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    
class DatabaseTableQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    database_id: Optional[UUID] = Field(Query(None, description="Database"))
    database_schema_id: Optional[UUID] = Field(Query(None, description="Schema"))
    layer_id: Optional[UUID] = Field(Query(None, description="Layer"))
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class DomainBaseModel(BaseModel):
    ...

class DomainCreateSchema(DomainBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class DomainUpdateSchema(DomainBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class DomainItemSchema(DomainBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class DomainListSchema(DomainBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    
class DomainQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class IAModelBaseModel(BaseModel):
    ...

class IAModelCreateSchema(IAModelBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: str = Field("0.0.0", description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    algorithm: Optional[str] = Field(None, description="Algoritmo usado")
    tecnology: Optional[str] = Field(None, description="Tecnologia usada para o modelo")
    server: Optional[str] = Field(None, description="URL do servidor usado para computar predições (inferência)")
    source: Optional[str] = Field(None, description="URL de onde está armazenado o modelo")

    # Associations
    domain_id: Optional[UUID] = None
    attributes: Optional[List["IAModelAttributeCreateSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterCreateSchema"]] = None
    results: Optional[List["IAModelResultCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelUpdateSchema(IAModelBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    algorithm: Optional[str] = Field(None, description="Algoritmo usado")
    tecnology: Optional[str] = Field(None, description="Tecnologia usada para o modelo")
    server: Optional[str] = Field(None, description="URL do servidor usado para computar predições (inferência)")
    source: Optional[str] = Field(None, description="URL de onde está armazenado o modelo")

    # Associations
    domain_id: Optional[UUID] = None
    attributes: Optional[List["IAModelAttributeUpdateSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterUpdateSchema"]] = None
    results: Optional[List["IAModelResultUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelItemSchema(IAModelBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")
    updated_by: Optional[str] = Field(None, description="Usuário que fez a atualização.")
    href: Optional[str] = Field(None, description="Link para o recurso correspondente a esta instância.")
    owner: Optional[str] = Field(None, description="Proprietário desta instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    algorithm: Optional[str] = Field(None, description="Algoritmo usado")
    tecnology: Optional[str] = Field(None, description="Tecnologia usada para o modelo")
    server: Optional[str] = Field(None, description="URL do servidor usado para computar predições (inferência)")
    source: Optional[str] = Field(None, description="URL de onde está armazenado o modelo")

    # Associations
    domain: Optional["DomainListSchema"] = None
    attributes: Optional[List["IAModelAttributeItemSchema"]] = None
    hyper_parameters: Optional[List["IAModelHyperParameterItemSchema"]] = None
    results: Optional[List["IAModelResultItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)
    

class IAModelListSchema(IAModelBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    fully_qualified_name: Optional[str] = Field(None, description="Nome que identifica exclusivamente a instância.")
    version: Optional[str] = Field(None, description="Versão de metadados da instância.")
    updated_at: Optional[datetime.datetime] = Field(None, description="Última hora de atualização.")

    model_config = ConfigDict(from_attributes=True)
    
class IAModelQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class IAModelAttributeBaseModel(BaseModel):
    ...

class IAModelAttributeCreateSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    usage: str = Field('feature', description="Uso do atributo no treinamento")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeUpdateSchema(IAModelAttributeBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    usage: Optional[str] = Field(None, description="Uso do atributo no treinamento")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeItemSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    usage: Optional[str] = Field(None, description="Uso do atributo no treinamento")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelAttributeListSchema(IAModelAttributeBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    usage: Optional[str] = Field(None, description="Uso do atributo no treinamento")

    model_config = ConfigDict(from_attributes=True)
    
class IAModelHyperParameterBaseModel(BaseModel):
    ...

class IAModelHyperParameterCreateSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    value: Optional[str] = Field(None, description="Valor do hiperparâmetro (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterUpdateSchema(IAModelHyperParameterBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    value: Optional[str] = Field(None, description="Valor do hiperparâmetro (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterItemSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    value: Optional[str] = Field(None, description="Valor do hiperparâmetro (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelHyperParameterListSchema(IAModelHyperParameterBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    value: Optional[str] = Field(None, description="Valor do hiperparâmetro (JSON)")

    model_config = ConfigDict(from_attributes=True)
    
class IAModelResultBaseModel(BaseModel):
    ...

class IAModelResultCreateSchema(IAModelResultBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    type: str = Field(..., description="Tipo do resultado")
    value: Optional[str] = Field(None, description="Valor do resultado (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultUpdateSchema(IAModelResultBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    type: Optional[str] = Field(None, description="Tipo do resultado")
    value: Optional[str] = Field(None, description="Valor do resultado (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultItemSchema(IAModelResultBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    type: Optional[str] = Field(None, description="Tipo do resultado")
    value: Optional[str] = Field(None, description="Valor do resultado (JSON)")

    model_config = ConfigDict(from_attributes=True)
    

class IAModelResultListSchema(IAModelResultBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    type: Optional[str] = Field(None, description="Tipo do resultado")
    value: Optional[str] = Field(None, description="Valor do resultado (JSON)")

    model_config = ConfigDict(from_attributes=True)
    
class LayerBaseModel(BaseModel):
    ...

class LayerCreateSchema(LayerBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class LayerUpdateSchema(LayerBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class LayerItemSchema(LayerBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    

class LayerListSchema(LayerBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")

    model_config = ConfigDict(from_attributes=True)
    
class LayerQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
class TableColumnBaseModel(BaseModel):
    ...

class TableColumnCreateSchema(TableColumnBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    display_name: str = Field(..., description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    data_type: DataType = Field(..., description="Tipo de dados da coluna (int, data etc.)")
    array_data_type: Optional[str] = Field(None, description="Tipo de dados do item do arranjo.")
    size: Optional[int] = Field(None, description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.")
    precision: Optional[int] = Field(None, description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.")
    scale: Optional[int] = Field(None, description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.")
    position: Optional[int] = Field(None, description="Posição ordinal da coluna na tabela.")
    primary_key: bool = Field(False, description="Coluna é chave-primária na tabela.")
    nullable: bool = Field(True, description="Coluna aceita valores nulos.")
    unique: bool = Field(False, description="Coluna é um índice UNIQUE.")
    is_metadata: bool = Field(False, description="Coluna é um metadado.")

    model_config = ConfigDict(from_attributes=True)
    

class TableColumnUpdateSchema(TableColumnBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    data_type: Optional[DataType] = Field(None, description="Tipo de dados da coluna (int, data etc.)")
    array_data_type: Optional[str] = Field(None, description="Tipo de dados do item do arranjo.")
    size: Optional[int] = Field(None, description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.")
    precision: Optional[int] = Field(None, description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.")
    scale: Optional[int] = Field(None, description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.")
    position: Optional[int] = Field(None, description="Posição ordinal da coluna na tabela.")
    primary_key: Optional[bool] = Field(None, description="Coluna é chave-primária na tabela.")
    nullable: Optional[bool] = Field(None, description="Coluna aceita valores nulos.")
    unique: Optional[bool] = Field(None, description="Coluna é um índice UNIQUE.")
    is_metadata: Optional[bool] = Field(None, description="Coluna é um metadado.")

    model_config = ConfigDict(from_attributes=True)
    

class TableColumnItemSchema(TableColumnBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    display_name: Optional[str] = Field(None, description="Nome de exibição que identifica a instância.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    data_type: Optional[DataType] = Field(None, description="Tipo de dados da coluna (int, data etc.)")
    array_data_type: Optional[str] = Field(None, description="Tipo de dados do item do arranjo.")
    size: Optional[int] = Field(None, description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.")
    precision: Optional[int] = Field(None, description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.")
    scale: Optional[int] = Field(None, description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.")
    position: Optional[int] = Field(None, description="Posição ordinal da coluna na tabela.")
    primary_key: Optional[bool] = Field(None, description="Coluna é chave-primária na tabela.")
    nullable: Optional[bool] = Field(None, description="Coluna aceita valores nulos.")
    unique: Optional[bool] = Field(None, description="Coluna é um índice UNIQUE.")
    is_metadata: Optional[bool] = Field(None, description="Coluna é um metadado.")

    model_config = ConfigDict(from_attributes=True)
    
class TagBaseModel(BaseModel):
    ...

class TagItemSchema(TagBaseModel):
    """ JSON serialization schema for serializing a single object"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    applicable_to: Optional[str] = Field(None, description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula")

    model_config = ConfigDict(from_attributes=True)
    

class TagListSchema(TagBaseModel):
    """ JSON serialization schema for serializing a list of objects"""
    id: Optional[UUID] = Field(None, description="Identificador")
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    applicable_to: Optional[str] = Field(None, description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula")

    model_config = ConfigDict(from_attributes=True)
    

class TagCreateSchema(TagBaseModel):
    """ JSON serialization schema for creating an instance"""
    name: str = Field(..., description="Nome da instância.")
    deleted: bool = Field(False, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    applicable_to: Optional[str] = Field(None, description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula")

    model_config = ConfigDict(from_attributes=True)
    

class TagUpdateSchema(TagBaseModel):
    """ Optional model for serialization of updating objects"""
    name: Optional[str] = Field(None, description="Nome da instância.")
    deleted: Optional[bool] = Field(None, description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.")
    description: Optional[str] = Field(None, description="Descrição da instância.")
    applicable_to: Optional[str] = Field(None, description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula")

    model_config = ConfigDict(from_attributes=True)
    
class TagQuerySchema(BaseQuerySchema):
    """ Used for querying data """
    query: Optional[str] = Field(Query(None, description="Consulta"))
    ...
