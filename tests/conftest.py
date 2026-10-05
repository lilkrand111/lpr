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
def get_test_session():
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