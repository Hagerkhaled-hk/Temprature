import datetime as dt

from tests.test_cities import make_city


def fake_two_days(monkeypatch):
    async def fake_fetch(latitude, longitude, days):
        return [
            {"date": dt.date(2026, 11, 1), "temp_max": 30.0, "temp_min": 18.0, "temp_mean": 24.0},
            {"date": dt.date(2026, 11, 2), "temp_max": 32.0, "temp_min": 20.0, "temp_mean": 26.0},
        ]

    monkeypatch.setattr("app.routers.temperatures.fetch_daily_temperatures", fake_fetch)


def test_sync_inserts_then_updates(client, monkeypatch):
    fake_two_days(monkeypatch)
    city_id = make_city(client)

    first = client.post(f"/cities/{city_id}/sync?days=2")
    assert first.json() == {"city_id": city_id, "inserted": 2, "updated": 0}

    second = client.post(f"/cities/{city_id}/sync?days=2")
    assert second.json() == {"city_id": city_id, "inserted": 0, "updated": 2}


def test_stats(client, monkeypatch):
    fake_two_days(monkeypatch)
    city_id = make_city(client)
    client.post(f"/cities/{city_id}/sync?days=2")

    stats = client.get(f"/cities/{city_id}/stats").json()
    assert stats["days"] == 2
    assert stats["avg_mean"] == 25.0
    assert stats["highest_max"] == 32.0
    assert stats["lowest_min"] == 18.0
    assert stats["hottest_day"] == "2026-11-02"


def test_stats_without_readings_returns_404(client):
    city_id = make_city(client)
    assert client.get(f"/cities/{city_id}/stats").status_code == 404


def test_invalid_date_range_returns_400(client):
    city_id = make_city(client)
    response = client.get(f"/cities/{city_id}/temperatures?start=2026-11-10&end=2026-11-01")
    assert response.status_code == 400


def test_sync_unknown_city_returns_404(client):
    assert client.post("/cities/999/sync").status_code == 404


def test_hottest_ranking(client, monkeypatch):
    async def fake_fetch(latitude, longitude, days):
        hot = 40.0 if latitude < 25 else 30.0  # Aswan (24.09) is hotter than Cairo (30.04)
        return [{"date": dt.date(2026, 11, 1), "temp_max": hot, "temp_min": 20.0, "temp_mean": 30.0}]

    monkeypatch.setattr("app.routers.temperatures.fetch_daily_temperatures", fake_fetch)
    cairo = make_city(client, "Cairo", lat=30.04, lon=31.24)
    aswan = make_city(client, "Aswan", lat=24.09, lon=32.90)
    client.post(f"/cities/{cairo}/sync")
    client.post(f"/cities/{aswan}/sync")

    ranking = client.get("/rankings/hottest?date=2026-11-01").json()
    assert [item["city"] for item in ranking] == ["Aswan", "Cairo"]