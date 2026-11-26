from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post("", response_model=schemas.CityOut, status_code=201)
def create_city(payload: schemas.CityCreate, db: Session = Depends(get_db)):
    city = models.City(**payload.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.get("", response_model=list[schemas.CityOut])
def list_cities(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(models.City)
    if search:
        stmt = stmt.where(models.City.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(models.City.name).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{city_id}", response_model=schemas.CityOut)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.get(models.City, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.delete("/{city_id}", status_code=204)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    city = db.get(models.City, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    db.delete(city)
    db.commit()