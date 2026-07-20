"""Symmetric encryption helpers for secrets stored at rest (social tokens)."""
import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet

from config.settings import get_settings


@lru_cache
def _fernet() -> Fernet:
    settings = get_settings()
    if settings.ENCRYPTION_KEY:
        key = settings.ENCRYPTION_KEY.encode()
    else:
        # Derive a stable Fernet key from SECRET_KEY so encryption works
        # out of the box; set ENCRYPTION_KEY explicitly to rotate independently.
        digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_value(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()
