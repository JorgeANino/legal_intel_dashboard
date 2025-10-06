"""
User model
"""
# Local application imports
from app.core.database import Base
from app.models.base import AuditMixin
# Third-party imports
from sqlalchemy import Boolean, Column, Integer, String


class User(Base, AuditMixin):
    """User model with audit fields"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
