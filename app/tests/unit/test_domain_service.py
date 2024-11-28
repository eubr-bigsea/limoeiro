import pytest
import datetime
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ...schemas import DomainCreateRequestSchema, DomainUpdateRequestSchema
from ...models import Domain
from ...database import Base
from ...services.domain_service import DomainService

@pytest.mark.asyncio
async def test_add_domain(domain_service, sample_domain_data):
    """Test adding a new domain"""
    domain = await domain_service.add(sample_domain_data)
    
    assert domain.id is not None
    assert domain.display_name == sample_domain_data.display_name
    assert domain.description == sample_domain_data.description

@pytest.mark.asyncio
async def test_get_domain(domain_service, sample_domain_data):
    """Test retrieving a domain by ID"""
    created_domain = await domain_service.add(sample_domain_data)
    retrieved_domain = await domain_service.get(created_domain.id)
    
    assert retrieved_domain is not None
    assert retrieved_domain.id == created_domain.id
    assert retrieved_domain.display_name == sample_domain_data.display_name

@pytest.mark.asyncio
async def test_delete_domain(domain_service, sample_domain_data):
    """Test deleting a domain"""
    created_domain = await domain_service.add(sample_domain_data)
    
    deleted_domain = await domain_service.delete(created_domain.id)
    assert deleted_domain.id == created_domain.id
    
    retrieved_domain = await domain_service.get(created_domain.id)
    assert retrieved_domain is None

@pytest.mark.asyncio
async def test_update_domain(domain_service, sample_domain_data):
    """Test updating a domain"""
    created_domain = await domain_service.add(sample_domain_data)
    
    updated_data = DomainUpdateRequestSchema(
        display_name="Updated Domain",
        description="Updated Description"
    )
    
    updated_domain = await domain_service.update(created_domain.id, updated_data)
    
    assert updated_domain is not None
    assert updated_domain.id == created_domain.id
    assert updated_domain.display_name == "Updated Domain"
    assert updated_domain.description == "Updated Description"

@pytest.mark.asyncio
async def test_find_domains(domain_service, sample_domain_data):
    """Test finding domains with pagination and sorting"""
    # Create multiple domains
    domains_to_create = [
        DomainCreateRequestSchema(
			name=f"Domain {i}",
			display_name=f"Domain {i}", description=f"Description {i}",
			fully_qualified_name=f"Domain {i}", updated_by="test",
			updated_at=datetime.datetime.now())
        for i in range(3)
    ]
    
    for domain_data in domains_to_create:
        await domain_service.add(domain_data)
    
    found_domains = await domain_service.find(
        sort="display_name",
        ascending=True,
        page=1,
        page_size=2
    )
    
    assert len(found_domains) == 2
    assert found_domains[0].display_name < found_domains[1].display_name

@pytest.mark.asyncio
async def test_get_nonexistent_domain(domain_service):
    """Test retrieving a non-existent domain"""
    non_existent_id = uuid.uuid4()
    domain = await domain_service.get(non_existent_id)
    assert domain is None

@pytest.mark.asyncio
async def test_update_nonexistent_domain(domain_service, sample_domain_data):
    """Test updating a non-existent domain"""
    non_existent_id = uuid.uuid4()
    updated_domain = await domain_service.update(non_existent_id, sample_domain_data)
    assert updated_domain is None
