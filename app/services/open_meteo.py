# الجلب من الـ API الخارجي
import datetime as dt

import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherServiceError(Exception):
    pass


async def fetch_daily_temperatures(latitude: float, longitude: float, days: int) -> list[dict]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
        "timezone": "auto",
        "past_days": days,
        "forecast_days": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise WeatherServiceError(f"Weather service failed: {exc}") from exc

    daily = response.json()["daily"]
    return [
        {"date": dt.date.fromisoformat(day), "temp_max": tmax, "temp_min": tmin, "temp_mean": tmean}
        for day, tmax, tmin, tmean in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["temperature_2m_mean"],
        )
    ]