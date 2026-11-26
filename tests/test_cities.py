def make_city(client, name="Cairo", country="Egypt", lat=30.04, lon=31.24):
    response = client.post(
        "/cities",
        json={"name": name, "country": country, "latitude": lat, "longitude": lon},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_city(client):
    city_id = make_city(client)
    response = client.get(f"/cities/{city_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Cairo"


def test_invalid_latitude_returns_422(client):
    response = client.post(
        "/cities",
        json={"name": "Nowhere", "country": "X", "latitude": 200, "longitude": 0},
    )
    assert response.status_code == 422


def test_city_not_found_returns_404(client):
    assert client.get("/cities/999").status_code == 404


def test_search_cities(client):
    make_city(client, "Cairo")
    make_city(client, "Aswan", lat=24.09, lon=32.90)
    response = client.get("/cities?search=asw")
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Aswan"]


def test_delete_city(client):
    city_id = make_city(client)
    assert client.delete(f"/cities/{city_id}").status_code == 204
    assert client.get(f"/cities/{city_id}").status_code == 404