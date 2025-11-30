from models.tag import Tag
from models.movie import Movie


def test_create_tag(client):
    movie_withot_tag = client.post(
        "/movies/",
        json={
            "title": "Interstellar",
            "genres": "Sci-Fi|Adventure",
        },
    )
    result_movie = movie_withot_tag.json()
    tag_payload = {
        "user_id": 1,
        "movie_id": result_movie["movie_id"],
        "tag": "Sci-Fi",
        "timestamp": 1625159073,
    }
    tag_response = client.post("/tags/", json=tag_payload)
    assert tag_response.status_code == 201
    tag_data = tag_response.json()
    assert tag_data["user_id"] == 1
    assert tag_data["movie_id"] == result_movie["movie_id"]
    assert tag_data["tag"] == "Sci-Fi"
    assert tag_data["timestamp"] == 1625159073


def test_create_tag_movie_not_found(client):
    tag_payload = {
        "user_id": 1,
        "movie_id": 9999,
        "tag": "Sci-Fi",
        "timestamp": 1625159073,
    }
    tag_response = client.post("/tags/", json=tag_payload)
    assert tag_response.status_code == 400


def test_duplicate_tag_same_movie(client, sample_tag):
    tag_payload = {
        "user_id": 1,
        "movie_id": sample_tag.movie_id,
        "tag": sample_tag.tag,
        "timestamp": 1625159073,
    }
    tag_response = client.post("/tags/", json=tag_payload)
    assert tag_response.status_code == 400


def test_read_tag(client, sample_tag):
    tag_response = client.get(f"/tags/{sample_tag.id}")
    assert tag_response.status_code == 200
    tag_data = tag_response.json()
    assert tag_data["user_id"] == sample_tag.user_id
    assert tag_data["movie_id"] == sample_tag.movie_id
    assert tag_data["tag"] == sample_tag.tag
    assert tag_data["timestamp"] == sample_tag.timestamp


def test_read_tag_not_found(client):
    response = client.get("/tags/9999")
    assert response.status_code == 404


def test_update_tag(client, db_session, sample_tag):
    tag_to_update_payload = {
        "id": sample_tag.id,
        "tag": "UpdatedTag",
        "timestamp": 1625259073,
    }
    response = client.put("/tags/", json=tag_to_update_payload)
    assert response.status_code == 200
    tag_data = response.json()
    assert tag_data["tag"] == "UpdatedTag"
    assert tag_data["timestamp"] == 1625259073
    updated_tag_db = db_session.query(Tag).filter(Tag.id == sample_tag.id).first()
    assert updated_tag_db.tag == "UpdatedTag"


def test_update_tag_not_found(client):
    tag_to_update_payload = {
        "id": 9999,
        "tag": "NonexistentTag",
        "timestamp": 1625259073,
    }
    response = client.put("/tags/", json=tag_to_update_payload)
    assert response.status_code == 404


def test_update_tag_duplicate_check(client, db_session, sample_tag):
    tag_b = Tag(
        user_id=1,
        movie_id=sample_tag.movie_id,
        tag="Tag B",
        timestamp=12345,
    )
    db_session.add(tag_b)
    db_session.commit()
    db_session.refresh(tag_b)
    payload = {"id": tag_b.id, "tag": sample_tag.tag, "timestamp": 123456}

    response = client.put("/tags/", json=payload)
    assert response.status_code == 400
    assert "Tag with this name already exists" in response.json()["detail"]


def test_delete_tag(client, db_session, sample_tag):
    delete_tag_payload = {"id": sample_tag.id}
    response = client.request("DELETE", "/tags/", json=delete_tag_payload)
    assert response.status_code == 200
    data = response.json()
    assert "Tag deleted successfully" in data["message"]
    deleted_tag = db_session.query(Tag).filter(Tag.id == sample_tag.id).first()
    assert deleted_tag is None


def test_delete_tag_not_found(client):
    delete_tag_payload = {"id": 9999}
    response = client.request("DELETE", "/tags/", json=delete_tag_payload)
    assert response.status_code == 404
