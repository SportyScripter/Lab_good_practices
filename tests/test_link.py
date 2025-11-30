from models.link import Link


def test_create_link(client, db_session, sample_movie):
    link_payload = {
        "movie_id": sample_movie.movie_id,
        "imbdld": "tt0816692",
        "tmdbld": "157336",
    }
    link_response = client.post("/links/", json=link_payload)
    assert link_response.status_code == 201
    link_data = link_response.json()
    assert link_data["movie_id"] == sample_movie.movie_id
    assert link_data["imbdld"] == "tt0816692"
    assert link_data["tmdbld"] == "157336"
    db_link = (
        db_session.query(Link).filter(Link.movie_id == sample_movie.movie_id).first()
    )
    assert db_link is not None


def test_read_link(client, sample_movie):
    link_payload = {
        "movie_id": sample_movie.movie_id,
        "imbdld": "tt0816692",
        "tmdbld": "157336",
    }
    link_response = client.post("/links/", json=link_payload)
    assert link_response.status_code == 201
    link_get_response = client.get(f"/links/{sample_movie.movie_id}")
    assert link_get_response.status_code == 200
    link_data = link_get_response.json()
    assert link_data["movie_id"] == sample_movie.movie_id
    assert link_data["imbdld"] == "tt0816692"
    assert link_data["tmdbld"] == "157336"


def test_read_link_not_found(client):
    response = client.get("/links/9999")
    assert response.status_code == 404


def test_update_link(client, db_session, sample_movie):
    link_payload = Link(
        movie_id=sample_movie.movie_id,
        imbdld="tt0816692",
        tmdbld="157336",
    )
    db_session.add(link_payload)
    db_session.commit()
    update_payload = {
        "movie_id": sample_movie.movie_id,
        "imbdld": "tt0816696",
        "tmdbld": "157337",
    }
    response = client.put("/links/", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["movie_id"] == sample_movie.movie_id
    assert data["imbdld"] == "tt0816696"
    updated_link = (
        db_session.query(Link).filter(Link.movie_id == sample_movie.movie_id).first()
    )
    assert updated_link.imbdld == "tt0816696"


def test_link_not_found_update(client):
    payload = {
        "movie_id": 9999,
        "imbdld": "tt9999999",
        "tmdbld": "999999",
    }
    response = client.put("/links/", json=payload)
    assert response.status_code == 404


def test_delete_link(client, db_session, sample_movie):
    link_payload = Link(
        movie_id=sample_movie.movie_id,
        imbdld="tt0816692",
        tmdbld="157336",
    )
    db_session.add(link_payload)
    db_session.commit()
    delete_response = client.request("DELETE", f"/links/{sample_movie.movie_id}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert "deleted successfully" in delete_data["message"]
    deleted_link = (
        db_session.query(Link).filter(Link.movie_id == sample_movie.movie_id).first()
    )
    assert deleted_link is None


def test_delete_link_not_found(client):
    response = client.request("DELETE", "/links/9999")
    assert response.status_code == 404
