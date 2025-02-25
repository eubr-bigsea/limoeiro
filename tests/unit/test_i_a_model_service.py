import pytest
import uuid
from app.schemas import IAModelCreateSchema, IAModelQuerySchema, IAModelUpdateSchema
from app.services.i_a_model_service import IAModelService

@pytest.mark.asyncio
async def test_add_i_a_model(i_a_model_service, sample_i_a_model_data):
    """Test adding a new i_a_model"""
    i_a_model = await i_a_model_service.add(sample_i_a_model_data)

    assert i_a_model.id is not None
    assert i_a_model.name == sample_i_a_model_data.name
    assert i_a_model.description == sample_i_a_model_data.description


@pytest.mark.asyncio
async def test_get_i_a_model(i_a_model_service, sample_i_a_model_data):
    """Test retrieving a i_a_model by ID"""
    created_i_a_model = await i_a_model_service.add(sample_i_a_model_data)
    retrieved_i_a_model = await i_a_model_service.get(created_i_a_model.id)

    assert retrieved_i_a_model is not None
    assert retrieved_i_a_model.id == created_i_a_model.id
    assert retrieved_i_a_model.name == sample_i_a_model_data.name


@pytest.mark.asyncio
async def test_delete_i_a_model(i_a_model_service, sample_i_a_model_data):
    """Test deleting a i_a_model"""
    created_i_a_model = await i_a_model_service.add(sample_i_a_model_data)

    deleted_i_a_model = await i_a_model_service.delete(created_i_a_model.id)
    assert deleted_i_a_model.id == created_i_a_model.id

    retrieved_i_a_model = await i_a_model_service.get(created_i_a_model.id)
    assert retrieved_i_a_model is None


@pytest.mark.asyncio
async def test_update_i_a_model(i_a_model_service, sample_i_a_model_data):
    """Test updating a i_a_model"""
    created_i_a_model = await i_a_model_service.add(sample_i_a_model_data)

    updated_data = IAModelUpdateSchema(
        name="Updated IAModel", deleted=False, description="Updated Description"
    )

    updated_i_a_model = await i_a_model_service.update(
        created_i_a_model.id, updated_data
    )

    assert updated_i_a_model is not None
    assert updated_i_a_model.id == created_i_a_model.id
    assert updated_i_a_model.name == "Updated IAModel"
    assert updated_i_a_model.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_i_a_models(
    i_a_model_service: IAModelService, sample_i_a_model_data
):
    """Test finding i_a_models with pagination and sorting"""
    # Create multiple i_a_models
    i_a_models_to_create = [
        IAModelCreateSchema(
            name=f"IAModel {i}",
            description=f"Description {i}",
            deleted=False,
            display_name=f"model {i}",
            fully_qualified_name=f"model {i}",
            updated_by="tester",
        )
        for i in range(3)
    ]

    for i_a_model_data in i_a_models_to_create:
        await i_a_model_service.add(i_a_model_data)

    opts = IAModelQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_i_a_models = await i_a_model_service.find(opts)

    assert len(found_i_a_models.items) == 2
    (i_a_model1, i_a_model2) = found_i_a_models.items
    assert i_a_model1.name < i_a_model2.name


@pytest.mark.asyncio
async def test_get_nonexistent_i_a_model(i_a_model_service):
    """Test retrieving a non-existent i_a_model"""
    non_existent_id = uuid.uuid4()
    i_a_model = await i_a_model_service.get(non_existent_id)
    assert i_a_model is None


@pytest.mark.asyncio
async def test_update_nonexistent_i_a_model(
    i_a_model_service, sample_i_a_model_data
):
    """Test updating a non-existent i_a_model"""
    non_existent_id = uuid.uuid4()
    updated_i_a_model = await i_a_model_service.update(
        non_existent_id, sample_i_a_model_data
    )
    assert updated_i_a_model is None
