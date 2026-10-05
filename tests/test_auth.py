from sqlalchemy import select
from backend.models import User
import pytest


def test_register(get_test_session):
    client = get_test_session
    response = client.post("/register", json={"email": "1@mail.com", "password": "123"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data['email'] == '1@mail.com'
    assert "password" not in data
    assert "hashed_password" not in data


def test_hashed_password(get_test_session, db_session):
    client = get_test_session
    client.post("/register", json={"email": "1@mail.com", "password": "123"})
    user = db_session.scalar(select(User).where(User.email == "1@mail.com"))
    assert user.hashed_password != "123"


def test_convert_email(get_test_session):
    client = get_test_session
    response = client.post("/register", json={"email": "Test@mail.com", "password": "123"})
    data = response.json()
    assert data['email'] == 'test@mail.com'


@pytest.mark.parametrize(
        "email",
        [('test@mail.com'), ('Test@mail.com')]
)
def test_dubl_email(get_test_session, email):
    client = get_test_session
    client.post("/register", json={"email": "test@mail.com", "password": "123"})
    response = client.post(
        "/register", json={"email": email, "password": "123"}
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload", [
    {"email": "1", "password": "1"},
    {"password": "1"},
    {"email": "test@mail.com"},
    {"email": "test@mail.com", "password": ""},
]
)
def test_incorrect_input(get_test_session, payload):
    client = get_test_session
    response = client.post('/register', json=payload)
    assert response.status_code == 422