# City Temperature API

A REST API built with FastAPI that stores cities and syncs their daily temperatures from the [Open-Meteo](https://open-meteo.com/) API, then serves them with statistics and rankings.

**Live docs:** https://YOUR-PROJECT.vercel.app/docs

## Features

- CRUD for cities (with validation of latitude/longitude)
- Sync daily max/min/mean temperatures from Open-Meteo (async, upsert by date)
- Query temperatures by date range
- Statistics per city (min, max, average) computed with pandas
- Ranking of the hottest cities for a given date
- Automatic interactive docs (Swagger UI)

## Tech Stack

FastAPI, SQLAlchemy 2.0, Pydantic, httpx, pandas, TiDB Cloud (MySQL), deployed on Vercel.

## Project Structure

```
app/
  main.py            # app entry point
  database.py        # engine, session, get_db dependency
  models.py          # SQLAlchemy models (City, TemperatureReading)
  schemas.py         # Pydantic schemas
  routers/           # cities and temperatures endpoints
  services/          # Open-Meteo client
```

## Main Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/cities` | Create a city |
| GET | `/cities` | List / search cities |
| GET | `/cities/{id}` | Get one city |
| DELETE | `/cities/{id}` | Delete a city |
| POST | `/cities/{id}/sync?days=7` | Fetch and store recent temperatures |
| GET | `/cities/{id}/temperatures` | Readings by date range |
| GET | `/cities/{id}/stats` | Min / max / average |
| GET | `/rankings/hottest` | Hottest cities on a date |
