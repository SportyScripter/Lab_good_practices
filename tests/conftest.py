import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from main import app
from db.config import Base, get_db
from models.movie import Movie
from models.rating import Rating
from models.tag import Tag
from models.link import Link

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_movie(db_session):
    movie = Movie(title="Titanic", genres="Romance|Drama")
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)
    return movie


@pytest.fixture
def sample_rating(db_session, sample_movie):
    rating = Rating(
        user_id=1, movie_id=sample_movie.movie_id, rating=5.0, timestamp=1625152800
    )
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating


@pytest.fixture
def sample_tag(db_session, sample_movie):
    tag = Tag(
        user_id=1,
        movie_id=sample_movie.movie_id,
        tag="Great Movie",
        timestamp=1625152800,
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag
