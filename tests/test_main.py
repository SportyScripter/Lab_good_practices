import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db
from models import Base
from auth import create_acces_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def ovveride_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = ovveride_get_db
    yield TestClient(app)


def test_login_success(client, db_session):
    from models import User
    from auth import get_password_hash

    user = User(
        username="testuser", hashed_password=get_password_hash("pass"), role="ROLE_USER"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/login", data={"username": user.username, "password": "pass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post(
        "/login", data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_create_user_as_admin(client, db_session):
    from models import User
    from auth import get_password_hash

    hashed = get_password_hash("adminpass")
    admin = User(username="admin", hashed_password=hashed, role="ROLE_ADMIN")
    db_session.add(admin)
    db_session.commit()

    admin_token = create_acces_token(data={"sub": "admin", "role": "ROLE_ADMIN"})
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpass"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_create_user_no_permission(client, db_session):
    from models import User
    from auth import get_password_hash

    hashed = get_password_hash("userpass")
    user = User(username="user", hashed_password=hashed, role="ROLE_USER")
    db_session.add(user)
    db_session.commit()

    user_token = create_acces_token(data={"sub": "user", "role": "ROLE_USER"})
    response = client.post(
        "/users",
        json={"username": "newuser", "password": "newpass"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_user_details(client, db_session):
    from models import User

    user = User(username="me", hashed_password="hashed", role="ROLE_USER")
    db_session.add(user)
    db_session.commit()

    token = create_acces_token(data={"sub": user.username, "role": user.role})

    response = client.get("/user_details", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "me"


def test_user_details_no_token(client):
    response = client.get("/user_details")
    assert response.status_code == 401


def test_register_public(client, db_session):
    response = client.post(
        "/register", json={"username": "nowy_ziomek", "password": "super_haslo"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "nowy_ziomek"
    assert response.json()["role"] == "ROLE_USER"
    from models import User

    user_in_db = db_session.query(User).filter(User.username == "nowy_ziomek").first()
    assert user_in_db is not None
