"""OAuth State model."""

from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class OAuthState(Base):
    """OAuth State model for CSRF protection during authorization flow."""

    __tablename__ = "oauth_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used = Column(Boolean, nullable=False, server_default="false")

    def __repr__(self):
        return f"<OAuthState(id={self.id}, state={self.state}, used={self.used})>"
