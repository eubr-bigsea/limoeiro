# Pattern to identify FQN vs UUID
import re
from uuid import UUID

from fastapi import HTTPException, Path

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)

def get_lookup_filter(
    entity_id: str = Path(
        ...,
        description="Entity identifier - can be either a UUID or an FQN (Fully Qualified Name)",
        examples={
            "uuid":
            {
                "name": "test",
                "summary": "Using UUID",
                "description": "Lookup by UUID primary key",
                "value": "123e4567-e89b-12d3-a456-426614174000",
            },
            "fqn":
            {

                "name": "test2",
                "summary": "Using FQN",
                "description": "Lookup by Fully Qualified Name",
                "value": "my.entity.name",
            },
        }, # type: ignore
    ),
):
    # Same implementation as before
    if UUID_PATTERN.match(entity_id):
        try:
            uuid_obj = UUID(entity_id)
            return uuid_obj
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")
    else:
        return entity_id
