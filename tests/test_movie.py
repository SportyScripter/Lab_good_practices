from models.movie import Movie


def test_read_movie_by_id(client, sample_movie):
    response = client.get(f"/movies/{sample_movie.movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == sample_movie.movie_id
    assert data["title"] == "Titanic"
    assert data["genres"] == "Romance|Drama"


def test_create_movie(client, db_session):
    payload = {"title": "The Matrix", "genres": "Sci-Fi"}
    response = client.post("/movies/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Matrix"
    assert "movie_id" in data
    db_movies = db_session.query(Movie).filter(Movie.title == "The Matrix").first()
    assert db_movies is not None
    assert db_movies.genres == "Sci-Fi"


def test_read_movie_not_found(client):
    response = client.get("/movies/9999")
    assert response.status_code == 404


def test_update_movie(client, sample_movie):
    payload = {
        "movie_id": sample_movie.movie_id,
        "title": "Shrek",
        "genres": "Animation",
    }
    response = client.put("/movies/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Shrek"
    assert data["genres"] == "Animation"


def test_update_movie_not_found(client):
    payload = {"title": "Nonexistent Movie", "genres": "Drama", "movie_id": 9999}
    response = client.put("/movies/", json=payload)
    assert response.status_code == 404


def test_delete_movie(client, db_session, sample_movie):
    payload = {"movie_id": sample_movie.movie_id}
    response = client.request("DELETE", "/movies/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Deleted successfully" in data["message"]
    deleted_movie = (
        db_session.query(Movie).filter(Movie.movie_id == sample_movie.movie_id).first()
    )
    assert deleted_movie is None


def test_delete_movie_not_found(client):
    payload = {"movie_id": 9999}
    response = client.request("DELETE", "/movies/", json=payload)
    assert response.status_code == 404
