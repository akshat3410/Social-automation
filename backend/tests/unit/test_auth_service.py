import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from config.settings import get_settings
from services.auth_service import ALGORITHM, AuthService
from services.exceptions import UnauthorizedError


def test_password_hash_and_verify():
    service = AuthService()
    hashed = service.hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert service.verify_password("correct horse battery staple", hashed)
    assert not service.verify_password("wrong password", hashed)


def test_verify_password_handles_garbage_hash():
    assert AuthService().verify_password("anything", "not-a-bcrypt-hash") is False


def test_token_round_trip():
    service = AuthService()
    user_id = uuid.uuid4()
    token = service.create_access_token(user_id)
    assert service.verify_token(token) == user_id


def test_tampered_token_rejected():
    service = AuthService()
    token = service.create_access_token(uuid.uuid4())
    with pytest.raises(UnauthorizedError):
        service.verify_token(token + "tampered")


def test_expired_token_rejected():
    service = AuthService()
    expired = jwt.encode(
        {
            "exp": datetime.now(UTC) - timedelta(minutes=5),
            "sub": str(uuid.uuid4()),
        },
        get_settings().SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(UnauthorizedError):
        service.verify_token(expired)


def test_token_signed_with_other_key_rejected():
    service = AuthService()
    forged = jwt.encode(
        {
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "sub": str(uuid.uuid4()),
        },
        "some-other-secret",
        algorithm=ALGORITHM,
    )
    with pytest.raises(UnauthorizedError):
        service.verify_token(forged)
