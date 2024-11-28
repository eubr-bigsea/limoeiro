from typing import Optional, Any, List
from http import HTTPStatus


class BaseApplicationException(Exception):
    """Base exception class for all application exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        cause: Optional[Exception] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.cause = cause
        self.details = details

    def __str__(self):
        base_message = super().__str__()
        if self.details:
            base_message = f"{base_message} - Details: {self.details}"
        if self.cause:
            base_message = f"{base_message} | Caused by: {self.cause}"
        return base_message


# Database Exceptions
class DatabaseException(BaseApplicationException):
    """Base class for database-related exceptions"""

    pass


class EntityNotFoundException(DatabaseException):
    """Raised when an entity is not found in the database"""

    def __init__(self, entity_type: str, entity_id: Any):
        super().__init__(
            message=f"{entity_type} with id {entity_id} not found",
            status_code=HTTPStatus.NOT_FOUND,
        )


class EntityAlreadyExistsException(DatabaseException):
    """Raised when attempting to create an entity that already exists"""

    def __init__(self, entity_type: str, identifier: Any):
        super().__init__(
            message=f"{entity_type} with identifier {identifier} already exists",
            status_code=HTTPStatus.CONFLICT,
        )


# Business Rule Exceptions
class BusinessRuleException(BaseApplicationException):
    """Base class for business rule violations"""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.UNPROCESSABLE_ENTITY,
        cause: Optional[Exception] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, status_code, cause, details)


class ValidationException(BusinessRuleException):
    """Raised when input validation fails"""

    def __init__(
        self, message: str = "Validation failed", details: Optional[dict] = None
    ):
        super().__init__(
            message=message, status_code=HTTPStatus.BAD_REQUEST, details=details
        )


# Bulk Operation Exceptions
class BulkOperationException(DatabaseException):
    """Raised when a bulk operation partially or completely fails"""

    def __init__(
        self,
        message: str,
        failed_items: List[dict],
        succeeded_items: List[dict],
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            status_code=HTTPStatus.MULTI_STATUS,
            cause=cause,
            details={
                "failed_items": failed_items,
                "succeeded_items": succeeded_items,
                "total_failed": len(failed_items),
                "total_succeeded": len(succeeded_items),
            },
        )
