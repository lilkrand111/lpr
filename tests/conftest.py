import pytest

from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.database import Base, get_session
from backend.main import app

TEST_DB_URL = make_url(settings.DB_URL).set(database="notes_test")
if not TEST_DB_URL.database.endswith("_test"):
    raise RuntimeError("ОПАСНО: имя тестовой базы должно заканчиваться на _test")
if TEST_DB_URL.database == make_url(settings.DB_URL).database:
    raise RuntimeError("ОПАСНО: тестовая база совпадает с рабочей базой")

test_engine = create_engine(TEST_DB_URL)
TestSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    def override_test_session():
        with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    with TestSessionLocal() as session:
        yield session


@pytest.fixture
def create_user(client):
    def _create(email="user@example.com", password="secret123"):
        response = client.post(
            "/register", json={"email": email, "password": password}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        return {"id": data["id"], "email": data["email"], "password": password}

    return _create


@pytest.fixture
def login(client):
    def _login(email, password):
        response = client.post(
            "/token", data={"username": email, "password": password}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        return {"Authorization": f"Bearer {data['access_token']}"}

    return _login


@pytest.fixture
def user_a(create_user):
    return create_user("a@example.com", "password-a")


@pytest.fixture
def user_b(create_user):
    return create_user("b@example.com", "password-b")


@pytest.fixture
def auth_a(user_a, login):
    return login(user_a["email"], user_a["password"])


@pytest.fixture
def auth_b(user_b, login):
    return login(user_b["email"], user_b["password"])
