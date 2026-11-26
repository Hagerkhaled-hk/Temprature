import datetime as dt
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.open_meteo import WeatherServiceError, fetch_daily_temperatures

router = APIRouter(tags=["temperatures"])


# ---------- helpers ----------

def _get_city_or_404(db: Session, city_id: int) -> models.City:
    city = db.get(models.City, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


def _check_range(start: Optional[dt.date], end: Optional[dt.date]) -> None:
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="start must be before or equal to end")


def _query_readings(db: Session, city_id: int, start: Optional[dt.date], end: Optional[dt.date]):
    stmt = select(models.TemperatureReading).where(models.TemperatureReading.city_id == city_id)
    if start:
        stmt = stmt.where(models.TemperatureReading.date >= start)
    if end:
        stmt = stmt.where(models.TemperatureReading.date <= end)
    return db.scalars(stmt.order_by(models.TemperatureReading.date)).all()


def _num(value) -> Optional[float]:
    return None if pd.isna(value) else round(float(value), 2)


# ---------- sync (data pipeline) ----------

@router.post("/cities/{city_id}/sync", response_model=schemas.SyncResult)
async def sync_city(
    city_id: int,
    days: int = Query(30, ge=1, le=92),
    db: Session = Depends(get_db),
):
    city = _get_city_or_404(db, city_id)

    try:
        rows = await fetch_daily_temperatures(city.latitude, city.longitude, days)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    existing = {
        r.date: r
        for r in db.scalars(
            select(models.TemperatureReading).where(
                models.TemperatureReading.city_id == city.id
            )
        )
    }

    inserted = updated = 0
    for row in rows:
        reading = existing.get(row["date"])
        if reading is None:
            db.add(models.TemperatureReading(city_id=city.id, **row))
            inserted += 1
        else:
            reading.temp_max = row["temp_max"]
            reading.temp_min = row["temp_min"]
            reading.temp_mean = row["temp_mean"]
            updated += 1

    db.commit()
    return schemas.SyncResult(city_id=city.id, inserted=inserted, updated=updated)


# ---------- readings ----------

@router.get("/cities/{city_id}/temperatures", response_model=list[schemas.TemperatureOut])
def list_temperatures(
    city_id: int,
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
    db: Session = Depends(get_db),
):
    _get_city_or_404(db, city_id)
    _check_range(start, end)
    return _query_readings(db, city_id, start, end)


# ---------- stats (pandas) ----------

@router.get("/cities/{city_id}/stats", response_model=schemas.StatsOut)
def city_stats(
    city_id: int,
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
    db: Session = Depends(get_db),
):
    _get_city_or_404(db, city_id)
    _check_range(start, end)
    readings = _query_readings(db, city_id, start, end)
    if not readings:
        raise HTTPException(status_code=404, detail="No readings for this period. Run /sync first.")

    df = pd.DataFrame(
        [
            {"date": r.date, "temp_max": r.temp_max, "temp_min": r.temp_min, "temp_mean": r.temp_mean}
            for r in readings
        ]
    )

    hottest_day = None
    if df["temp_max"].notna().any():
        hottest_day = df.loc[df["temp_max"].idxmax(), "date"]

    return schemas.StatsOut(
        city_id=city_id,
        start=df["date"].min(),
        end=df["date"].max(),
        days=len(df),
        avg_mean=_num(df["temp_mean"].mean()),
        highest_max=_num(df["temp_max"].max()),
        lowest_min=_num(df["temp_min"].min()),
        hottest_day=hottest_day,
    )


# ---------- ranking ----------

@router.get("/rankings/hottest", response_model=list[schemas.RankingItem])
def hottest_cities(
    date: dt.date,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            models.City.id,
            models.City.name,
            models.City.country,
            models.TemperatureReading.temp_max,
        )
        .join(models.TemperatureReading, models.TemperatureReading.city_id == models.City.id)
        .where(
            models.TemperatureReading.date == date,
            models.TemperatureReading.temp_max.is_not(None),
        )
        .order_by(models.TemperatureReading.temp_max.desc())
        .limit(limit)
    )
    return [
        schemas.RankingItem(city_id=r.id, city=r.name, country=r.country, temp_max=r.temp_max)
        for r in db.execute(stmt).all()
    ]