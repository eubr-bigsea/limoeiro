import pytest
import uuid

from app.exceptions import EntityNotFoundException
from app.schemas import TagCreateSchema, TagQuerySchema, TagUpdateSchema
from app.services.tag_service import TagService


@pytest.mark.asyncio
async def test_add_tag(tag_service, sample_tag_data):
    """Test adding a new tag"""
    tag = await tag_service.add(sample_tag_data)

    assert tag.id is not None
    assert tag.name == sample_tag_data.name
    assert tag.description == sample_tag_data.description


@pytest.mark.asyncio
async def test_get_tag(tag_service, sample_tag_data):
    """Test retrieving a tag by ID"""
    created_tag = await tag_service.add(sample_tag_data)
    retrieved_tag = await tag_service.get(created_tag.id)

    assert retrieved_tag is not None
    assert retrieved_tag.id == created_tag.id
    assert retrieved_tag.name == sample_tag_data.name


@pytest.mark.asyncio
async def test_delete_tag(tag_service, sample_tag_data):
    """Test deleting a tag"""
    created_tag = await tag_service.add(sample_tag_data)

    deleted_tag = await tag_service.delete(created_tag.id)
    assert deleted_tag.id == created_tag.id

    with pytest.raises(EntityNotFoundException) as nfe:
        await tag_service.get(created_tag.id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_tag(tag_service, sample_tag_data):
    """Test updating a tag"""
    created_tag = await tag_service.add(sample_tag_data)

    updated_data = TagUpdateSchema(
        name="Updated Tag", deleted=False, description="Updated Description"
    )

    updated_tag = await tag_service.update(created_tag.id, updated_data)

    assert updated_tag is not None
    assert updated_tag.id == created_tag.id
    assert updated_tag.name == "Updated Tag"
    assert updated_tag.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_tags(tag_service: TagService, sample_tag_data):
    """Test finding tags with pagination and sorting"""
    # Create multiple tags
    tags_to_create = [
        TagCreateSchema(
            name=f"Tag {i}",
            description=f"Description {i}",
            deleted=False,
        )
        for i in range(3)
    ]

    for tag_data in tags_to_create:
        await tag_service.add(tag_data)

    opts = TagQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_tags = await tag_service.find(opts)

    assert len(found_tags.items) == 2
    (tag1, tag2) = found_tags.items
    assert (
        tag1.name is not None and tag2.name is not None and tag1.name < tag2.name
    )


@pytest.mark.asyncio
async def test_get_nonexistent_tag(tag_service):
    """Test retrieving a non-existent tag"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await tag_service.get(non_existent_id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_tag(tag_service, sample_tag_data):
    """Test updating a non-existent tag"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await tag_service.update(non_existent_id, sample_tag_data)
    assert "not found" in str(nfe.value)
