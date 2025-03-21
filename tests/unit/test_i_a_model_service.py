import pytest
import uuid
from app.schemas import AIModelCreateSchema, AIModelQuerySchema, AIModelUpdateSchema
from app.services.a_i_model_service import AIModelService

@pytest.mark.asyncio
async def test_add_a_i_model(a_i_model_service, sample_a_i_model_data):
    """Test adding a new a_i_model"""
    a_i_model = await a_i_model_service.add(sample_a_i_model_data)

    assert a_i_model.id is not None
    assert a_i_model.name == sample_a_i_model_data.name
    assert a_i_model.description == sample_a_i_model_data.description


@pytest.mark.asyncio
async def test_get_a_i_model(a_i_model_service, sample_a_i_model_data):
    """Test retrieving a a_i_model by ID"""
    created_a_i_model = await a_i_model_service.add(sample_a_i_model_data)
    retrieved_a_i_model = await a_i_model_service.get(created_a_i_model.id)

    assert retrieved_a_i_model is not None
    assert retrieved_a_i_model.id == created_a_i_model.id
    assert retrieved_a_i_model.name == sample_a_i_model_data.name


@pytest.mark.asyncio
async def test_delete_a_i_model(a_i_model_service, sample_a_i_model_data):
    """Test deleting a a_i_model"""
    created_a_i_model = await a_i_model_service.add(sample_a_i_model_data)

    deleted_a_i_model = await a_i_model_service.delete(created_a_i_model.id)
    assert deleted_a_i_model.id == created_a_i_model.id

    retrieved_a_i_model = await a_i_model_service.get(created_a_i_model.id)
    assert retrieved_a_i_model is None


@pytest.mark.asyncio
async def test_update_a_i_model(a_i_model_service, sample_a_i_model_data):
    """Test updating a a_i_model"""
    created_a_i_model = await a_i_model_service.add(sample_a_i_model_data)

    updated_data = AIModelUpdateSchema(
        name="Updated AIModel", deleted=False, description="Updated Description"
    )

    updated_a_i_model = await a_i_model_service.update(
        created_a_i_model.id, updated_data
    )

    assert updated_a_i_model is not None
    assert updated_a_i_model.id == created_a_i_model.id
    assert updated_a_i_model.name == "Updated AIModel"
    assert updated_a_i_model.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_a_i_models(
    a_i_model_service: AIModelService, sample_a_i_model_data
):
    """Test finding a_i_models with pagination and sorting"""
    # Create multiple a_i_models
    a_i_models_to_create = [
        AIModelCreateSchema(
            name=f"AIModel {i}",
            description=f"Description {i}",
            deleted=False,
            display_name=f"model {i}",
            fully_qualified_name=f"model {i}",
            updated_by="tester",
        )
        for i in range(3)
    ]

    for a_i_model_data in a_i_models_to_create:
        await a_i_model_service.add(a_i_model_data)

    opts = AIModelQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_a_i_models = await a_i_model_service.find(opts)

    assert len(found_a_i_models.items) == 2
    (a_i_model1, a_i_model2) = found_a_i_models.items
    assert a_i_model1.name < a_i_model2.name


@pytest.mark.asyncio
async def test_get_nonexistent_a_i_model(a_i_model_service):
    """Test retrieving a non-existent a_i_model"""
    non_existent_id = uuid.uuid4()
    a_i_model = await a_i_model_service.get(non_existent_id)
    assert a_i_model is None


@pytest.mark.asyncio
async def test_update_nonexistent_a_i_model(
    a_i_model_service, sample_a_i_model_data
):
    """Test updating a non-existent a_i_model"""
    non_existent_id = uuid.uuid4()
    updated_a_i_model = await a_i_model_service.update(
        non_existent_id, sample_a_i_model_data
    )
    assert updated_a_i_model is None
