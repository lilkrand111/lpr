from sqlalchemy import select
from backend.models import User
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from backend.config import settings


def test_register(client):
    response = client.post("/register", json={"email": "1@mail.com", "password": "123"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "1@mail.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_hashed_password(client, db_session):
    client.post("/register", json={"email": "1@mail.com", "password": "123"})
    user = db_session.scalar(select(User).where(User.email == "1@mail.com"))
    assert user.hashed_password != "123"


def test_convert_email(client):
    response = client.post(
        "/register", json={"email": "Test@mail.com", "password": "123"}
    )
    data = response.json()
    assert data["email"] == "test@mail.com"


@pytest.mark.parametrize("email", [("test@mail.com"), ("Test@mail.com")])
def test_dubl_email(client, email):
    response = client.post("/register", json={"email": "test@mail.com", "password": "123"})
    assert response.status_code == 201
    response = client.post("/register", json={"email": email, "password": "123"})
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "1", "password": "1"},
        {"password": "1"},
        {"email": "test@mail.com"},
        {"email": "test@mail.com", "password": ""},
    ],
)
def test_incorrect_input(client, payload):
    response = client.post("/register", json=payload)
    assert response.status_code == 422


def test_success_login(client, user_a):
    response = client.post(
        "/token", data={"username": user_a["email"], "password": user_a["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    notes = client.get("/notes", headers=headers)
    assert notes.status_code == 200
    assert notes.json() == []


def test_email_uppercase(client, user_a):
    response = client.post(
        "/token", data={"username": "A@example.COM", "password": user_a["password"]}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_incorrect_password(client, user_a):
    response = client.post(
        "/token", data={"username": user_a["email"], "password": "123"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_incorrect_user(client, user_a):
    response1 = client.post(
        "/token", data={"username": user_a["email"], "password": "123"}
    )
    assert response1.status_code == 401
    response2 = client.post(
        "/token", data={"username": "c@example.com", "password": user_a["password"]}
    )
    assert response2.status_code == 401
    assert response1.json()["detail"] == response2.json()["detail"]


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ["POST", "/notes", {"title": "1", "content": "1"}],
        ["GET", "/notes", None],
        ["GET", "/notes/1", None],
        ["PUT", "/notes/1", {"title": "1", "content": "1"}],
        ["DELETE", "/notes/1", None],
    ],
)
def test_requests_without_token(client, method, path, body):
    response = client.request(method, path, json=body)
    assert response.status_code == 401


def _foreign_token():
    return jwt.encode(
        {
            "sub": "a@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "x" * 32,
        algorithm="HS256",
    )


@pytest.mark.parametrize("token", [("not.a.jwt"), (_foreign_token())])
def test_incorrect_token(client, user_a, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes", headers=headers)
    assert response.status_code == 401


def test_expires_token(client, user_a):
    payload = {
        "sub": user_a["email"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes", headers=headers)
    assert response.status_code == 401


def test_correct_token(client, user_a):
    payload = {
        "sub": user_a["email"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes", headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        {
            "sub": "ghost@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
    ],
)
def test_incorrect_payload(client, payload):
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes", headers=headers)
    assert response.status_code == 401
