 # جداول الـ DB (SQLAlchemy)
import datetime as dt
from typing import Optional 

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from sqlalchemy import String


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(100))  
    latitude: Mapped[float]
    longitude: Mapped[float]

    readings: Mapped[list["TemperatureReading"]] = relationship(
        back_populates="city", cascade="all, delete-orphan"
    )


class TemperatureReading(Base):
    __tablename__ = "temperature_readings"
    __table_args__ = (UniqueConstraint("city_id", "date", name="uq_city_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    date: Mapped[dt.date]
    temp_max: Mapped[Optional[float]]
    temp_min: Mapped[Optional[float]]
    temp_mean: Mapped[Optional[float]]

    city: Mapped["City"] = relationship(back_populates="readings")