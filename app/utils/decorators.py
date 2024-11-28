import functools
import logging
from typing import TypeVar, Callable, Any
from sqlalchemy.exc import SQLAlchemyError

from ..exceptions import DatabaseException

log = logging.getLogger(__name__)

T = TypeVar("T")


def handle_db_exceptions(
    error_message: str = "Database operation failed",
    status_code: int = 500,
) -> Callable:
    """
    Decorator to handle database exceptions uniformly.

    Args:
        error_message: Custom error message for the exception
        status_code: HTTP status code to use in case of error

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except DatabaseException:
                # Re-raise DatabaseExceptions without modification
                raise
            except SQLAlchemyError as e:
                log.error(f"Database error in {func.__name__}: {str(e)}")
                raise DatabaseException(
                    message=error_message, status_code=status_code, cause=e
                )

        return wrapper

    return decorator


def transactional(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle database transactions.
    Commits on success, rolls back on error.

    Returns:
        Callable: Decorated function
    """

    @functools.wraps(func)
    async def wrapper(self, *args: Any, **kwargs: Any) -> T:
        try:
            result = await func(self, *args, **kwargs)
            await self._session.commit()
            return result
        except Exception:
            await self._session.rollback()
            raise

    return wrapper
