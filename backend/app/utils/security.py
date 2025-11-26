"""Security utilities for token encryption and session management."""

import secrets
import time
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet
from app.config import settings


# Initialize Fernet cipher
cipher = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())


def generate_state() -> str:
    """Generate a cryptographically secure random state parameter.

    Returns:
        Random URL-safe token string
    """
    return secrets.token_urlsafe(32)


def create_signed_state(state: str, expires_in_seconds: int = 600) -> str:
    """Create a signed state value with expiry timestamp.

    Args:
        state: The state value to sign
        expires_in_seconds: How long until the state expires (default 10 minutes)

    Returns:
        Signed state string: base64(state|expiry|signature)
    """
    expiry = int(time.time()) + expires_in_seconds
    message = f"{state}|{expiry}"
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    combined = f"{message}|{signature}"
    return base64.urlsafe_b64encode(combined.encode()).decode()


def verify_signed_state(signed_state: str) -> str:
    """Verify a signed state and return the original state value.

    Args:
        signed_state: The signed state string from cookie

    Returns:
        Original state value if valid

    Raises:
        ValueError: If signature invalid or expired
    """
    try:
        decoded = base64.urlsafe_b64decode(signed_state.encode()).decode()
        parts = decoded.split("|")
        if len(parts) != 3:
            raise ValueError("Invalid state format")

        state, expiry_str, signature = parts
        expiry = int(expiry_str)

        # Check expiry
        if time.time() > expiry:
            raise ValueError("State has expired")

        # Verify signature
        message = f"{state}|{expiry_str}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid signature")

        return state
    except Exception as e:
        raise ValueError(f"Invalid signed state: {str(e)}")


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
