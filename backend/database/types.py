"""Custom SQLAlchemy column types."""
from sqlalchemy import String, TypeDecorator

from core.security import decrypt_value, encrypt_value


class EncryptedString(TypeDecorator[str]):
    """Stores string values encrypted at rest with Fernet."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        return encrypt_value(value)

    def process_result_value(self, value: str | None, dialect: object) -> str | None:
        if value is None:
            return None
        return decrypt_value(value)
