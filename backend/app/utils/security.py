"""Security utilities for token encryption and session management."""

import secrets
import uuid
from cryptography.fernet import Fernet
from app.config import settings


# Initialize Fernet cipher
cipher = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())


def generate_state() -> str:
    """Generate a random state parameter for CSRF protection.

    Returns:
        Random UUID string
    """
    return str(uuid.uuid4())


def generate_session_token() -> str:
    """Generate a secure random session token.

    Returns:
        Random token string (URL-safe)
    """
    return secrets.token_urlsafe(32)


def encrypt_token(token: str) -> str:
    """Encrypt a token using Fernet encryption.

    Args:
        token: Plain text token to encrypt

    Returns:
        Encrypted token as string
    """
    if not token:
        return ""
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token using Fernet encryption.

    Args:
        encrypted_token: Encrypted token string

    Returns:
        Decrypted plain text token
    """
    if not encrypted_token:
        return ""
    return cipher.decrypt(encrypted_token.encode()).decode()
