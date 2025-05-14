import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def client():
    # Use a single in-memory SQLite database connection for the test
    TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    connection = engine.connect()
    # Bind the sessionmaker to the same connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    # Create tables on the same connection
    Base.metadata.create_all(bind=connection)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Cleanup
    Base.metadata.drop_all(bind=connection)
    connection.close()
    engine.dispose()

def test_save_person(client):
    response = client.post(
        "/save",
        json={
            "external_id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "John Doe",
            "email": "john@example.com",
            "date_of_birth": "2020-01-01T12:12:34+00:00"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "external_id" in data
    assert "saved" in data["message"]
    # Test getting the person
    person_id = data["external_id"]
    response = client.get(f"/{person_id}")
    assert response.status_code == 200
    person_data = response.json()
    assert person_data["external_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert person_data["name"] == "John Doe"
    assert person_data["email"] == "john@example.com"
    assert person_data["date_of_birth"].startswith("2020-01-01T12:12:34") # timezone is not checked

def test_get_nonexistent_person(client):
    # Invalid UUID format should return 400
    response = client.get("/nonexistent")
    assert response.status_code == 400
    assert "uuid" in response.json()["detail"].lower()

    # Valid UUID but not in DB should return 404
    valid_but_missing = "123e4567-e89b-12d3-a456-426614174999"
    response = client.get(f"/{valid_but_missing}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
