# شكل الـ request والـ response (Pydantic)
from pydantic import BaseModel, ConfigDict, Field
import datetime as dt
from typing import Optional

class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CityOut(CityCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
class SyncResult(BaseModel):
    city_id: int
    inserted: int
    updated: int
    
    
class TemperatureOut(BaseModel):
    date: dt.date
    temp_max: Optional[float]
    temp_min: Optional[float]
    temp_mean: Optional[float]
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    city_id: int
    start: dt.date
    end: dt.date
    days: int
    avg_mean: Optional[float]
    highest_max: Optional[float]
    lowest_min: Optional[float]
    hottest_day: Optional[dt.date]


class RankingItem(BaseModel):
    city_id: int
    city: str
    country: str
    temp_max: float    