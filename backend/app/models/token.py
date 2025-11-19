"""Token model."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Token(Base):
    """Token model for storing OAuth access and refresh tokens."""

    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_type = Column(String(50), nullable=False, server_default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scopes = Column(JSONB, nullable=False, server_default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<Token(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
