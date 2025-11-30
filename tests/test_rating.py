from models.rating import Rating


def test_create_rating(client, db_session, sample_movie):
    rating_payload = {
        "user_id": 1,
        "movie_id": sample_movie.movie_id,
        "rating_value": 4.5,
        "timestamp": 1625159073,
    }
    rating_response = client.post("/ratings/", json=rating_payload)
    assert rating_response.status_code == 201
    rating_data = rating_response.json()
    assert rating_data["user_id"] == 1
    assert rating_data["movie_id"] == sample_movie.movie_id
    assert rating_data["rating"] == 4.5
    db_rating = (
        db_session.query(Rating)
        .filter(
            Rating.user_id == 1,
            Rating.movie_id == sample_movie.movie_id,
        )
        .first()
    )
    assert db_rating is not None


def test_create_rating_movie_not_found(client):
    rating_payload = {
        "user_id": 1,
        "movie_id": 9999,
        "rating_value": 4.5,
        "timestamp": 1625159073,
    }
    rating_response = client.post("/ratings/", json=rating_payload)
    assert rating_response.status_code == 404


def test_read_rating(client, sample_movie, sample_rating):
    rating_response = client.get(f"/ratings/{sample_rating.id}")
    assert rating_response.status_code == 200
    rating_data = rating_response.json()
    assert rating_data["user_id"] == sample_rating.user_id
    assert rating_data["movie_id"] == sample_movie.movie_id
    assert rating_data["rating"] == sample_rating.rating


def test_read_rating_not_found(client):
    response = client.get("/ratings/9999")
    assert response.status_code == 404


def test_update_rating(client, sample_movie, sample_rating):
    rating_to_update_payload = {
        "user_id": sample_rating.user_id,
        "movie_id": sample_movie.movie_id,
        "rating_value": 3.5,
        "timestamp": 1625259073,
    }
    response = client.put("/ratings/", json=rating_to_update_payload)
    assert response.status_code == 200
    rating_data = response.json()
    assert rating_data["rating"] == 3.5
    assert rating_data["timestamp"] == 1625259073


def test_update_rating_not_found_by_user_id(client, sample_movie):
    rating_to_update_payload = {
        "user_id": 9999,
        "movie_id": sample_movie.movie_id,
        "rating_value": 3.5,
        "timestamp": 1625259073,
    }
    response = client.put("/ratings/", json=rating_to_update_payload)
    assert response.status_code == 404


def test_update_rating_not_found_by_movie_id(client, sample_rating):
    rating_to_update_payload = {
        "user_id": sample_rating.user_id,
        "movie_id": 999999,
        "rating_value": 3.5,
        "timestamp": 1625259073,
    }
    response = client.put("/ratings/", json=rating_to_update_payload)
    assert response.status_code == 404


def test_delete_rating(client, sample_rating):
    response = client.request(
        "DELETE", "/ratings/", json={"movie_id": sample_rating.movie_id}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_rating_not_found(client):
    response = client.request("DELETE", "/ratings/", json={"movie_id": 9999})
    assert response.status_code == 404
