import datetime
from uuid import UUID
from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel, Field, ConfigDict

from .models import LinkType
from .models import TableType
from .models import DataType

M = TypeVar("M")


class PaginatedSchema(BaseModel, Generic[M]):
    """Used for pagination"""

    page_size: int = Field(description="Tamanho da página")
    page_count: int = Field(description="Total de páginas")
    page: int = Field(description="Número da página")
    count: int = Field(description="Número de itens retornados na resposta")
    items: List[M] = Field(description=("Lista de itens retornados"))

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseQuerySchema(BaseModel):
    """Used for querying data"""

    page: int = Field(default=1, description="Número da página")
    page_size: int = Field(default=20, description="Número de itens por página")

    # Field selection
    include_fields: Optional[str] = Field(
        default=None, description="Campos a serem incluídos na resposa"
    )
    exclude_fields: Optional[str] = Field(
        default=None, description="Campos a serem excluídos da resposta"
    )

    # Sorting
    sort_by: Optional[str] = Field(
        default=None, description="Opção de ordenação"
    )
    sort_order: Optional[str] = Field(
        default=None,
        description="Ordenação ascendente ou descendente",
        pattern="^(asc|desc)$",
    )


class ResponsibilityTypeBaseModel(BaseModel): ...


class ResponsibilityTypeItemSchema(ResponsibilityTypeBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class ResponsibilityTypeListSchema(ResponsibilityTypeBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class AssetLinkBaseModel(BaseModel): ...


class AssetLinkCreateSchema(AssetLinkBaseModel):
    """JSON serialization schema for creating an instance"""

    url: Optional[str] = Field(
        default=None,
        description="Url para o recurso correspondente a esta instância.",
    )
    type: LinkType = Field(description="Tipo do link")

    # Associations
    asset: "AssetCreateSchema"

    model_config = ConfigDict(from_attributes=True)


class AssetLinkUpdateSchema(AssetLinkBaseModel):
    """Optional model for serialization of updating objects"""

    url: Optional[str] = Field(
        default=None,
        description="Url para o recurso correspondente a esta instância.",
    )
    type: Optional[LinkType] = Field(default=None, description="Tipo do link")

    # Associations
    asset: Optional["AssetListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class AssetLinkItemSchema(AssetLinkBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    url: Optional[str] = Field(
        default=None,
        description="Url para o recurso correspondente a esta instância.",
    )
    type: Optional[LinkType] = Field(default=None, description="Tipo do link")

    # Associations
    asset: Optional["AssetListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class AssetLinkListSchema(AssetLinkBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    url: Optional[str] = Field(
        default=None,
        description="Url para o recurso correspondente a esta instância.",
    )
    type: Optional[LinkType] = Field(default=None, description="Tipo do link")

    # Associations
    asset: Optional["AssetListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class LayerBaseModel(BaseModel): ...


class LayerCreateSchema(LayerBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class LayerUpdateSchema(LayerBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class LayerItemSchema(LayerBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class LayerListSchema(LayerBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class LayerQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class DomainBaseModel(BaseModel): ...


class DomainCreateSchema(DomainBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class DomainUpdateSchema(DomainBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class DomainItemSchema(DomainBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class DomainListSchema(DomainBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )

    model_config = ConfigDict(from_attributes=True)


class DomainQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class DatabaseProviderTypeBaseModel(BaseModel): ...


class DatabaseProviderTypeItemSchema(DatabaseProviderTypeBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[str] = None
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    image: Optional[str] = Field(
        default=None, description="Imagem do tipo de provedor"
    )

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderTypeListSchema(DatabaseProviderTypeBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[str] = None
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    image: Optional[str] = Field(
        default=None, description="Imagem do tipo de provedor"
    )

    model_config = ConfigDict(from_attributes=True)


class TagBaseModel(BaseModel): ...


class TagItemSchema(TagBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    applicable_to: Optional[str] = Field(
        default=None,
        description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula",
    )

    model_config = ConfigDict(from_attributes=True)


class TagListSchema(TagBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    applicable_to: Optional[str] = Field(
        default=None,
        description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula",
    )

    model_config = ConfigDict(from_attributes=True)


class TagCreateSchema(TagBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    applicable_to: Optional[str] = Field(
        default=None,
        description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula",
    )

    model_config = ConfigDict(from_attributes=True)


class TagUpdateSchema(TagBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    applicable_to: Optional[str] = Field(
        default=None,
        description="Aplicável a qual tipo de entidade. Lista de tipos separados por vírgula",
    )

    model_config = ConfigDict(from_attributes=True)


class TagQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class AssetBaseModel(BaseModel): ...


class AssetCreateSchema(AssetBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    fully_qualified_name: str = Field(
        description="Nome que identifica exclusivamente a instância."
    )
    display_name: str = Field(
        description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    notes: Optional[str] = Field(default=None, description="Observação.")
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    version: Optional[str] = Field(
        default=None, description="Versão de metadados da instância."
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    updated_by: Optional[str] = Field(
        default=None, description="Usuário que fez a atualização."
    )

    # Associations
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    links: Optional[List["AssetLinkCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AssetUpdateSchema(AssetBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(
        default=None,
        description="Nome que identifica exclusivamente a instância.",
    )
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    notes: Optional[str] = Field(default=None, description="Observação.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    version: Optional[str] = Field(
        default=None, description="Versão de metadados da instância."
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    updated_by: Optional[str] = Field(
        default=None, description="Usuário que fez a atualização."
    )

    # Associations
    domain_id: Optional[UUID] = None
    layer_id: Optional[UUID] = None
    links: Optional[List["AssetLinkUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AssetItemSchema(AssetBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    fully_qualified_name: Optional[str] = Field(
        default=None,
        description="Nome que identifica exclusivamente a instância.",
    )
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    notes: Optional[str] = Field(default=None, description="Observação.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    version: Optional[str] = Field(
        default=None, description="Versão de metadados da instância."
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    updated_by: Optional[str] = Field(
        default=None, description="Usuário que fez a atualização."
    )

    # Associations
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None
    links: Optional[List["AssetLinkItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AssetListSchema(AssetBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    fully_qualified_name: Optional[str] = Field(
        default=None,
        description="Nome que identifica exclusivamente a instância.",
    )
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    version: Optional[str] = Field(
        default=None, description="Versão de metadados da instância."
    )
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )

    # Associations
    domain: Optional["DomainListSchema"] = None
    layer: Optional["LayerListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderBaseModel(BaseModel): ...


class DatabaseProviderCreateSchema(AssetCreateSchema, DatabaseProviderBaseModel):
    """JSON serialization schema for creating an instance"""

    configuration: Optional[str] = Field(
        default=None, description="Configuração"
    )

    # Associations
    provider_type_id: str
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderUpdateSchema(AssetUpdateSchema, DatabaseProviderBaseModel):
    """Optional model for serialization of updating objects"""

    configuration: Optional[str] = Field(
        default=None, description="Configuração"
    )

    # Associations
    provider_type_id: Optional[str] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderItemSchema(AssetItemSchema, DatabaseProviderBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    configuration: Optional[str] = Field(
        default=None, description="Configuração"
    )

    # Associations
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    connection_id: Optional[UUID] = None
    ingestions: Optional[List["DatabaseProviderIngestionItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderListSchema(AssetListSchema, DatabaseProviderBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    # Associations
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    provider_type: Optional["DatabaseProviderTypeListSchema"] = None
    connection_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    provider_type_id: Optional[str] = Field(
        default=None, description="Provider type"
    )
    domain_id: Optional[UUID] = Field(default=None, description="Domain")
    layer_id: Optional[UUID] = Field(default=None, description="Layer")
    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class DatabaseProviderConnectionBaseModel(BaseModel): ...


class DatabaseProviderConnectionCreateSchema(
    DatabaseProviderConnectionBaseModel
):
    """JSON serialization schema for creating an instance"""

    user_name: str = Field(description="Nome do usuário / login")
    password: Optional[str] = Field(default=None, description="Senha do usuário")
    host: str = Field(description="Nome do servidor")
    port: int = Field(description="Porta do servidor")
    database: Optional[str] = Field(default=None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(
        default=None, description="Parâmetros extras"
    )

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderConnectionUpdateSchema(
    DatabaseProviderConnectionBaseModel
):
    """Optional model for serialization of updating objects"""

    user_name: Optional[str] = Field(
        default=None, description="Nome do usuário / login"
    )
    password: Optional[str] = Field(default=None, description="Senha do usuário")
    host: Optional[str] = Field(default=None, description="Nome do servidor")
    port: Optional[int] = Field(default=None, description="Porta do servidor")
    database: Optional[str] = Field(default=None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(
        default=None, description="Parâmetros extras"
    )

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderConnectionItemSchema(DatabaseProviderConnectionBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    user_name: Optional[str] = Field(
        default=None, description="Nome do usuário / login"
    )
    password: Optional[str] = Field(default=None, description="Senha do usuário")
    host: Optional[str] = Field(default=None, description="Nome do servidor")
    port: Optional[int] = Field(default=None, description="Porta do servidor")
    database: Optional[str] = Field(default=None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(
        default=None, description="Parâmetros extras"
    )

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderConnectionListSchema(DatabaseProviderConnectionBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    user_name: Optional[str] = Field(
        default=None, description="Nome do usuário / login"
    )
    password: Optional[str] = Field(default=None, description="Senha do usuário")
    host: Optional[str] = Field(default=None, description="Nome do servidor")
    port: Optional[int] = Field(default=None, description="Porta do servidor")
    database: Optional[str] = Field(default=None, description="Banco de dados")
    extra_parameters: Optional[str] = Field(
        default=None, description="Parâmetros extras"
    )

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderConnectionQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    provider_id: Optional[str] = Field(default=None, description="Provider")
    ...

class Scheduling(BaseModel):
    expression: str

class DatabaseProviderIngestionBaseModel(BaseModel): ...


class DatabaseProviderIngestionCreateSchema(DatabaseProviderIngestionBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    type: str = Field(description="Tipo de ingestão")
    include_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem incluídas na ingestão",
    )
    exclude_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem excluídas da ingestão",
    )
    include_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem incluídos na ingestão",
    )
    exclude_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem excluídos da ingestão",
    )
    include_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem incluídas na ingestão",
    )
    exclude_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem excluídas da ingestão",
    )
    include_view: bool = Field(
        default=False, description="Considerar views na ingestão"
    )
    override_mode: Optional[str] = Field(
        default=None, description="Opção para sobrescrita"
    )
    scheduling: Optional[Scheduling] = Field(default=None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(
        default=None, description="Status das últimas execuções"
    )
    retries: int = Field(default=5, description="Max retries")

    # Associations
    provider_id: UUID
    logs: Optional[List["DatabaseProviderIngestionLogCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionUpdateSchema(DatabaseProviderIngestionBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    type: Optional[str] = Field(default=None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem incluídas na ingestão",
    )
    exclude_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem excluídas da ingestão",
    )
    include_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem incluídos na ingestão",
    )
    exclude_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem excluídos da ingestão",
    )
    include_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem incluídas na ingestão",
    )
    exclude_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem excluídas da ingestão",
    )
    include_view: Optional[bool] = Field(
        default=None, description="Considerar views na ingestão"
    )
    override_mode: Optional[str] = Field(
        default=None, description="Opção para sobrescrita"
    )
    scheduling: Optional[Scheduling] = Field(default=None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(
        default=None, description="Status das últimas execuções"
    )
    retries: Optional[int] = Field(default=None, description="Max retries")

    # Associations
    provider_id: Optional[UUID] = None
    logs: Optional[List["DatabaseProviderIngestionLogUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionItemSchema(DatabaseProviderIngestionBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    type: Optional[str] = Field(default=None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem incluídas na ingestão",
    )
    exclude_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem excluídas da ingestão",
    )
    include_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem incluídos na ingestão",
    )
    exclude_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem excluídos da ingestão",
    )
    include_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem incluídas na ingestão",
    )
    exclude_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem excluídas da ingestão",
    )
    include_view: Optional[bool] = Field(
        default=None, description="Considerar views na ingestão"
    )
    override_mode: Optional[str] = Field(
        default=None, description="Opção para sobrescrita"
    )
    scheduling: Optional[Scheduling] = Field(default=None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(
        default=None, description="Status das últimas execuções"
    )
    retries: Optional[int] = Field(default=None, description="Max retries")

    # Associations
    provider_id: Optional[UUID] = None
    logs: Optional[List["DatabaseProviderIngestionLogItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionListSchema(DatabaseProviderIngestionBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    type: Optional[str] = Field(default=None, description="Tipo de ingestão")
    include_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem incluídas na ingestão",
    )
    exclude_database: Optional[str] = Field(
        default=None,
        description="Expressão regular para as bases a serem excluídas da ingestão",
    )
    include_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem incluídos na ingestão",
    )
    exclude_schema: Optional[str] = Field(
        default=None,
        description="Expressão regular para os esquemas a serem excluídos da ingestão",
    )
    include_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem incluídas na ingestão",
    )
    exclude_table: Optional[str] = Field(
        default=None,
        description="Expressão regular para as tabelas a serem excluídas da ingestão",
    )
    include_view: Optional[bool] = Field(
        default=None, description="Considerar views na ingestão"
    )
    override_mode: Optional[str] = Field(
        default=None, description="Opção para sobrescrita"
    )
    scheduling: Optional[Scheduling] = Field(default=None, description="Agendamento")
    recent_runs_statuses: Optional[str] = Field(
        default=None, description="Status das últimas execuções"
    )
    retries: Optional[int] = Field(default=None, description="Max retries")

    # Associations
    provider_id: Optional[UUID] = None
    logs: Optional[List["DatabaseProviderIngestionLogListSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    provider_id: Optional[str] = Field(default=None, description="Provider")
    ...


class DatabaseProviderIngestionLogBaseModel(BaseModel): ...


class DatabaseProviderIngestionLogCreateSchema(
    DatabaseProviderIngestionLogBaseModel
):
    """JSON serialization schema for creating an instance"""

    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    status: str = Field(description="Status de execução")
    log: Optional[str] = Field(default=None, description="Log de execução")

    # Associations
    ingestion_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionLogUpdateSchema(
    DatabaseProviderIngestionLogBaseModel
):
    """Optional model for serialization of updating objects"""

    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    status: Optional[str] = Field(default=None, description="Status de execução")
    log: Optional[str] = Field(default=None, description="Log de execução")

    # Associations
    ingestion_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionLogItemSchema(
    DatabaseProviderIngestionLogBaseModel
):
    """JSON serialization schema for serializing a single object"""

    id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    status: Optional[str] = Field(default=None, description="Status de execução")
    log: Optional[str] = Field(default=None, description="Log de execução")

    model_config = ConfigDict(from_attributes=True)


class DatabaseProviderIngestionLogListSchema(
    DatabaseProviderIngestionLogBaseModel
):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = Field(
        default=None, description="Última hora de atualização."
    )
    status: Optional[str] = Field(default=None, description="Status de execução")
    log: Optional[str] = Field(default=None, description="Log de execução")

    model_config = ConfigDict(from_attributes=True)


class DatabaseBaseModel(BaseModel): ...


class DatabaseCreateSchema(AssetCreateSchema, DatabaseBaseModel):
    """JSON serialization schema for creating an instance"""

    retention_period: Optional[str] = Field(
        default=None,
        description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.",
    )

    # Associations
    provider_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DatabaseUpdateSchema(AssetUpdateSchema, DatabaseBaseModel):
    """Optional model for serialization of updating objects"""

    retention_period: Optional[str] = Field(
        default=None,
        description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.",
    )

    # Associations
    provider_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseItemSchema(AssetItemSchema, DatabaseBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    retention_period: Optional[str] = Field(
        default=None,
        description="Período de retenção dos dados no banco de dados. O período é expresso como duração no formato ISO 8601 em UTC. Exemplo - P23DT23H.",
    )

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseListSchema(AssetListSchema, DatabaseBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    # Associations
    provider: Optional["DatabaseProviderListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    provider_id: Optional[str] = Field(default=None, description="Provider")
    domain_id: Optional[UUID] = Field(default=None, description="Domínio")
    layer_id: Optional[UUID] = Field(default=None, description="Camada")
    query: Optional[str] = Field(default=None, description="Consulta")
    tags: Optional[str] = Field(default=None, description="Tags")
    ...


class DatabaseSchemaBaseModel(BaseModel): ...


class DatabaseSchemaCreateSchema(AssetCreateSchema, DatabaseSchemaBaseModel):
    """JSON serialization schema for creating an instance"""

    # Associations
    database_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DatabaseSchemaUpdateSchema(AssetUpdateSchema, DatabaseSchemaBaseModel):
    """Optional model for serialization of updating objects"""

    # Associations
    database_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseSchemaItemSchema(AssetItemSchema, DatabaseSchemaBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    # Associations
    database: Optional["DatabaseListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseSchemaListSchema(AssetListSchema, DatabaseSchemaBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    # Associations
    database: Optional["DatabaseListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseSchemaQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    database_id: Optional[UUID] = Field(default=None, description="Database")
    layer_id: Optional[UUID] = Field(default=None, description="Camada")
    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class DatabaseTableBaseModel(BaseModel): ...


class DatabaseTableCreateSchema(AssetCreateSchema, DatabaseTableBaseModel):
    """JSON serialization schema for creating an instance"""

    type: TableType = Field(default="REGULAR", description="Tipo da tabela")
    proxy_enabled: bool = Field(
        default=False, description="Indica se a tabela está disponível no proxy."
    )
    query: Optional[str] = Field(
        default=None,
        description="Consulta para gerar os dados, se for uma VIEW.",
    )
    cache_type: Optional[str] = Field(
        default=None, description="Tipo de cache para a tabela."
    )
    cache_ttl_in_seconds: Optional[int] = Field(
        default=None, description="Tempo de validade do cache da tabela."
    )
    cache_validation: Optional[str] = Field(
        default=None, description="Comando para validar o cache"
    )

    # Associations
    database_id: UUID
    database_schema_id: UUID
    columns: Optional[List["TableColumnCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableUpdateSchema(AssetUpdateSchema, DatabaseTableBaseModel):
    """Optional model for serialization of updating objects"""

    type: Optional[TableType] = Field(default=None, description="Tipo da tabela")
    proxy_enabled: Optional[bool] = Field(
        default=None, description="Indica se a tabela está disponível no proxy."
    )
    query: Optional[str] = Field(
        default=None,
        description="Consulta para gerar os dados, se for uma VIEW.",
    )
    cache_type: Optional[str] = Field(
        default=None, description="Tipo de cache para a tabela."
    )
    cache_ttl_in_seconds: Optional[int] = Field(
        default=None, description="Tempo de validade do cache da tabela."
    )
    cache_validation: Optional[str] = Field(
        default=None, description="Comando para validar o cache"
    )

    # Associations
    database_id: Optional[UUID] = None
    database_schema_id: Optional[UUID] = None
    columns: Optional[List["TableColumnUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableItemSchema(AssetItemSchema, DatabaseTableBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    type: Optional[TableType] = Field(default=None, description="Tipo da tabela")
    proxy_enabled: Optional[bool] = Field(
        default=None, description="Indica se a tabela está disponível no proxy."
    )
    query: Optional[str] = Field(
        default=None,
        description="Consulta para gerar os dados, se for uma VIEW.",
    )
    cache_type: Optional[str] = Field(
        default=None, description="Tipo de cache para a tabela."
    )
    cache_ttl_in_seconds: Optional[int] = Field(
        default=None, description="Tempo de validade do cache da tabela."
    )
    cache_validation: Optional[str] = Field(
        default=None, description="Comando para validar o cache"
    )

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None
    columns: Optional[List["TableColumnItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableListSchema(AssetListSchema, DatabaseTableBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    # Associations
    database_schema: Optional["DatabaseSchemaListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    database_id: Optional[UUID] = Field(default=None, description="Database")
    database_schema_id: Optional[UUID] = Field(
        default=None, description="Schema"
    )
    layer_id: Optional[UUID] = Field(default=None, description="Layer")
    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class DatabaseTableSampleBaseModel(BaseModel): ...


class DatabaseTableSampleCreateSchema(DatabaseTableSampleBaseModel):
    """JSON serialization schema for creating an instance"""

    date: datetime.datetime = Field(description="Data e hora da amosrta")
    content: str = Field(description="Conteúdo da amostra (JSON).")
    is_visible: bool = Field(
        default=True, description="Amostra pode ser visualizada"
    )

    # Associations
    database_table_id: UUID

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableSampleUpdateSchema(DatabaseTableSampleBaseModel):
    """Optional model for serialization of updating objects"""

    date: Optional[datetime.datetime] = Field(
        default=None, description="Data e hora da amosrta"
    )
    content: Optional[str] = Field(
        default=None, description="Conteúdo da amostra (JSON)."
    )
    is_visible: Optional[bool] = Field(
        default=None, description="Amostra pode ser visualizada"
    )

    # Associations
    database_table_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableSampleItemSchema(DatabaseTableSampleBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    date: Optional[datetime.datetime] = Field(
        default=None, description="Data e hora da amosrta"
    )
    content: Optional[str] = Field(
        default=None, description="Conteúdo da amostra (JSON)."
    )
    is_visible: Optional[bool] = Field(
        default=None, description="Amostra pode ser visualizada"
    )

    # Associations
    database_table: Optional["DatabaseTableListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseTableSampleListSchema(DatabaseTableSampleBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    date: Optional[datetime.datetime] = Field(
        default=None, description="Data e hora da amosrta"
    )
    content: Optional[str] = Field(
        default=None, description="Conteúdo da amostra (JSON)."
    )
    is_visible: Optional[bool] = Field(
        default=None, description="Amostra pode ser visualizada"
    )

    # Associations
    database_table: Optional["DatabaseTableListSchema"] = None

    model_config = ConfigDict(from_attributes=True)


class TableColumnBaseModel(BaseModel): ...


class TableColumnCreateSchema(TableColumnBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    display_name: str = Field(
        description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    data_type: DataType = Field(
        description="Tipo de dados da coluna (int, data etc.)"
    )
    array_data_type: Optional[str] = Field(
        default=None, description="Tipo de dados do item do arranjo."
    )
    size: Optional[int] = Field(
        default=None,
        description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.",
    )
    precision: Optional[int] = Field(
        default=None,
        description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.",
    )
    scale: Optional[int] = Field(
        default=None,
        description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.",
    )
    position: Optional[int] = Field(
        default=None, description="Posição ordinal da coluna na tabela."
    )
    primary_key: bool = Field(
        default=False, description="Coluna é chave-primária na tabela."
    )
    nullable: bool = Field(
        default=True, description="Coluna aceita valores nulos."
    )
    unique: bool = Field(default=False, description="Coluna é um índice UNIQUE.")
    is_metadata: bool = Field(default=False, description="Coluna é um metadado.")

    model_config = ConfigDict(from_attributes=True)


class TableColumnUpdateSchema(TableColumnBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    data_type: Optional[DataType] = Field(
        default=None, description="Tipo de dados da coluna (int, data etc.)"
    )
    array_data_type: Optional[str] = Field(
        default=None, description="Tipo de dados do item do arranjo."
    )
    size: Optional[int] = Field(
        default=None,
        description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.",
    )
    precision: Optional[int] = Field(
        default=None,
        description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.",
    )
    scale: Optional[int] = Field(
        default=None,
        description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.",
    )
    position: Optional[int] = Field(
        default=None, description="Posição ordinal da coluna na tabela."
    )
    primary_key: Optional[bool] = Field(
        default=None, description="Coluna é chave-primária na tabela."
    )
    nullable: Optional[bool] = Field(
        default=None, description="Coluna aceita valores nulos."
    )
    unique: Optional[bool] = Field(
        default=None, description="Coluna é um índice UNIQUE."
    )
    is_metadata: Optional[bool] = Field(
        default=None, description="Coluna é um metadado."
    )

    model_config = ConfigDict(from_attributes=True)


class TableColumnItemSchema(TableColumnBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    display_name: Optional[str] = Field(
        default=None, description="Nome de exibição que identifica a instância."
    )
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    data_type: Optional[DataType] = Field(
        default=None, description="Tipo de dados da coluna (int, data etc.)"
    )
    array_data_type: Optional[str] = Field(
        default=None, description="Tipo de dados do item do arranjo."
    )
    size: Optional[int] = Field(
        default=None,
        description="Comprimento de char, varchar, binary, varbinary dataTypes, senão nulo.",
    )
    precision: Optional[int] = Field(
        default=None,
        description="A precisão de um numérico é a contagem total de dígitos significativos no número inteiro.",
    )
    scale: Optional[int] = Field(
        default=None,
        description="A escala de um numérico é a contagem de dígitos decimais na parte fracionária, à direita do ponto decimal.",
    )
    position: Optional[int] = Field(
        default=None, description="Posição ordinal da coluna na tabela."
    )
    primary_key: Optional[bool] = Field(
        default=None, description="Coluna é chave-primária na tabela."
    )
    nullable: Optional[bool] = Field(
        default=None, description="Coluna aceita valores nulos."
    )
    unique: Optional[bool] = Field(
        default=None, description="Coluna é um índice UNIQUE."
    )
    is_metadata: Optional[bool] = Field(
        default=None, description="Coluna é um metadado."
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelBaseModel(BaseModel): ...


class AIModelCreateSchema(AssetCreateSchema, AIModelBaseModel):
    """JSON serialization schema for creating an instance"""

    type: str = Field(description="Tipo de modelo")
    algorithms: Optional[str] = Field(
        default=None, description="Algoritmos usado"
    )
    technologies: Optional[str] = Field(
        default=None, description="Tecnologias usada para o modelo"
    )
    server: Optional[str] = Field(
        default=None,
        description="URL do servidor usado para computar predições (inferência)",
    )
    source: Optional[str] = Field(
        default=None, description="URL de onde está armazenado o modelo"
    )

    # Associations
    attributes: Optional[List["AIModelAttributeCreateSchema"]] = None
    hyper_parameters: Optional[List["AIModelHyperParameterCreateSchema"]] = None
    results: Optional[List["AIModelResultCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AIModelUpdateSchema(AssetUpdateSchema, AIModelBaseModel):
    """Optional model for serialization of updating objects"""

    type: Optional[str] = Field(default=None, description="Tipo de modelo")
    algorithms: Optional[str] = Field(
        default=None, description="Algoritmos usado"
    )
    technologies: Optional[str] = Field(
        default=None, description="Tecnologias usada para o modelo"
    )
    server: Optional[str] = Field(
        default=None,
        description="URL do servidor usado para computar predições (inferência)",
    )
    source: Optional[str] = Field(
        default=None, description="URL de onde está armazenado o modelo"
    )

    # Associations
    attributes: Optional[List["AIModelAttributeUpdateSchema"]] = None
    hyper_parameters: Optional[List["AIModelHyperParameterUpdateSchema"]] = None
    results: Optional[List["AIModelResultUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AIModelItemSchema(AssetItemSchema, AIModelBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    type: Optional[str] = Field(default=None, description="Tipo de modelo")
    algorithms: Optional[str] = Field(
        default=None, description="Algoritmos usado"
    )
    technologies: Optional[str] = Field(
        default=None, description="Tecnologias usada para o modelo"
    )
    server: Optional[str] = Field(
        default=None,
        description="URL do servidor usado para computar predições (inferência)",
    )
    source: Optional[str] = Field(
        default=None, description="URL de onde está armazenado o modelo"
    )

    # Associations
    attributes: Optional[List["AIModelAttributeItemSchema"]] = None
    hyper_parameters: Optional[List["AIModelHyperParameterItemSchema"]] = None
    results: Optional[List["AIModelResultItemSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class AIModelListSchema(AssetListSchema, AIModelBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")

    model_config = ConfigDict(from_attributes=True)


class AIModelQuerySchema(BaseQuerySchema):
    """Used for querying data"""

    query: Optional[str] = Field(default=None, description="Consulta")
    ...


class AIModelAttributeBaseModel(BaseModel): ...


class AIModelAttributeCreateSchema(AIModelAttributeBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: bool = Field(
        default=False,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    usage: str = Field(
        default="feature", description="Uso do atributo no treinamento"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelAttributeUpdateSchema(AIModelAttributeBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    usage: Optional[str] = Field(
        default=None, description="Uso do atributo no treinamento"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelAttributeItemSchema(AIModelAttributeBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    usage: Optional[str] = Field(
        default=None, description="Uso do atributo no treinamento"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelAttributeListSchema(AIModelAttributeBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    deleted: Optional[bool] = Field(
        default=None,
        description="Quando true, indica que a entidade foi excluída temporariamente. Padrão: False.",
    )
    usage: Optional[str] = Field(
        default=None, description="Uso do atributo no treinamento"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelHyperParameterBaseModel(BaseModel): ...


class AIModelHyperParameterCreateSchema(AIModelHyperParameterBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    value: Optional[str] = Field(
        default=None, description="Valor do hiperparâmetro (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelHyperParameterUpdateSchema(AIModelHyperParameterBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    value: Optional[str] = Field(
        default=None, description="Valor do hiperparâmetro (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelHyperParameterItemSchema(AIModelHyperParameterBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    value: Optional[str] = Field(
        default=None, description="Valor do hiperparâmetro (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelHyperParameterListSchema(AIModelHyperParameterBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    description: Optional[str] = Field(
        default=None, description="Descrição da instância."
    )
    value: Optional[str] = Field(
        default=None, description="Valor do hiperparâmetro (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelResultBaseModel(BaseModel): ...


class AIModelResultCreateSchema(AIModelResultBaseModel):
    """JSON serialization schema for creating an instance"""

    name: str = Field(description="Nome da instância.")
    type: str = Field(description="Tipo do resultado")
    value: Optional[str] = Field(
        default=None, description="Valor do resultado (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelResultUpdateSchema(AIModelResultBaseModel):
    """Optional model for serialization of updating objects"""

    name: Optional[str] = Field(default=None, description="Nome da instância.")
    type: Optional[str] = Field(default=None, description="Tipo do resultado")
    value: Optional[str] = Field(
        default=None, description="Valor do resultado (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelResultItemSchema(AIModelResultBaseModel):
    """JSON serialization schema for serializing a single object"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    type: Optional[str] = Field(default=None, description="Tipo do resultado")
    value: Optional[str] = Field(
        default=None, description="Valor do resultado (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)


class AIModelResultListSchema(AIModelResultBaseModel):
    """JSON serialization schema for serializing a list of objects"""

    id: Optional[UUID] = Field(default=None, description="Identificador")
    name: Optional[str] = Field(default=None, description="Nome da instância.")
    type: Optional[str] = Field(default=None, description="Tipo do resultado")
    value: Optional[str] = Field(
        default=None, description="Valor do resultado (JSON)"
    )

    model_config = ConfigDict(from_attributes=True)
