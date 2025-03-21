import pytest
import uuid
from app.exceptions import EntityNotFoundException
from app.schemas import LayerCreateSchema, LayerQuerySchema, LayerUpdateSchema
from app.services.layer_service import LayerService


@pytest.mark.asyncio
async def test_add_layer(layer_service, sample_layer_data):
    """Test adding a new layer"""
    layer = await layer_service.add(sample_layer_data)

    assert layer.id is not None
    assert layer.name == sample_layer_data.name
    assert layer.description == sample_layer_data.description


@pytest.mark.asyncio
async def test_get_layer(layer_service, sample_layer_data):
    """Test retrieving a layer by ID"""
    created_layer = await layer_service.add(sample_layer_data)
    retrieved_layer = await layer_service.get(created_layer.id)

    assert retrieved_layer is not None
    assert retrieved_layer.id == created_layer.id
    assert retrieved_layer.name == sample_layer_data.name


@pytest.mark.asyncio
async def test_delete_layer(layer_service, sample_layer_data):
    """Test deleting a layer"""
    created_layer = await layer_service.add(sample_layer_data)

    deleted_layer = await layer_service.delete(created_layer.id)
    assert deleted_layer.id == created_layer.id
    with pytest.raises(EntityNotFoundException) as nfe:
        await layer_service.get(created_layer.id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_layer(layer_service, sample_layer_data):
    """Test updating a layer"""
    created_layer = await layer_service.add(sample_layer_data)

    updated_data = LayerUpdateSchema(
        name="Updated Layer", deleted=False, description="Updated Description"
    )

    updated_layer = await layer_service.update(created_layer.id, updated_data)

    assert updated_layer is not None
    assert updated_layer.id == created_layer.id
    assert updated_layer.name == "Updated Layer"
    assert updated_layer.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_layers(layer_service: LayerService, sample_layer_data):
    """Test finding layers with pagination and sorting"""
    # Create multiple layers
    layers_to_create = [
        LayerCreateSchema(
            name=f"Layer {i}",
            description=f"Description {i}",
            deleted=False,
        )
        for i in range(3)
    ]

    for layer_data in layers_to_create:
        await layer_service.add(layer_data)

    opts = LayerQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_layers = await layer_service.find(opts)

    assert len(found_layers.items) == 2
    (layer1, layer2) = found_layers.items
    assert (
        layer1.name is not None
        and layer2.name is not None
        and layer1.name < layer2.name
    )


@pytest.mark.asyncio
async def test_get_nonexistent_layer(layer_service):
    """Test retrieving a non-existent layer"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await layer_service.get(non_existent_id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_layer(layer_service, sample_layer_data):
    """Test updating a non-existent layer"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await layer_service.update(non_existent_id, sample_layer_data)
    assert "not found" in str(nfe.value)
