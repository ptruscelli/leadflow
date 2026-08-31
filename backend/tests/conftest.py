import pytest 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.deps import get_db, require_session
from app.main import app
from app.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite://" # in-memory db

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# swap get_db for a throwaway SQLite database

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_require_session():
    # return string email just like the real require_session dependency would
    return "test@example.com"



@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    # dependency overrides to allow tests to run with no session cookie and with a test db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_session] = override_require_session

    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)



@pytest.fixture
def unauthorized_client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    # don't override require_session dependency
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)