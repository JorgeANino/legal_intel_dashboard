"""
Base model classes with audit fields
"""
# Third-party imports
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func


class AuditMixin:
    """
    Mixin class that provides audit fields for tracking creation, updates, and soft deletes
    """

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)  # User ID who created the record
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    updated_by = Column(Integer, nullable=True)  # User ID who last updated the record
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete timestamp
    deleted_by = Column(Integer, nullable=True)  # User ID who deleted the record

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted"""
        return self.deleted_at is not None

    def soft_delete(self, deleted_by: int | None = None) -> None:
        """
        Soft delete the record by setting deleted_at timestamp

        Args:
            deleted_by: User ID who is performing the deletion
        """
        # Standard library imports
        from datetime import datetime

        self.deleted_at = datetime.now()  # type: ignore[assignment]
        self.deleted_by = deleted_by  # type: ignore[assignment]

    def restore(self) -> None:
        """Restore a soft deleted record"""
        self.deleted_at = None  # type: ignore[assignment]
        self.deleted_by = None  # type: ignore[assignment]
