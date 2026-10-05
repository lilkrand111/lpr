from backend.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from datetime import datetime, timezone
import jwt


def test_get_password_hash():
    hashed = get_password_hash("test")
    assert hashed != "test"
    assert hashed.startswith("$argon2")


def test_salt_in_get_password_hash():
    assert get_password_hash("test") != get_password_hash("test")


def test_verify_password():
    assert (
        verify_password(
            "test",
            "$argon2id$v=19$m=65536,t=3,p=4$je4NklkKQN11wNxetwpc8w$rgOC9rNNgGr24TqffQoB7AeH3Jq4bJoSjh+MOHbSz0w",
        )
        == True
    )
    assert (
        verify_password(
            "test",
            "$argon2id$v=19$m=65536,t=3,p=4$+PggKx1Khm//dnWsEJDmMg$+PVIQUgV0F5GbaBeT9SK8Fn/48SaQ2hnO8Er2jC7yGE",
        )
        == False
    )


def test_create_access_token():
    data = {"sub": "Andrey"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "Andrey"
    assert payload.get("exp") > datetime.now(timezone.utc).timestamp()
