from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Destination(BaseModel):
    postal_code: str
    street: str
    city: str
    state: str
    country: str
    reference: Optional[str] = None
    observation: Optional[str] = None


class TripBase(BaseModel):
    name: str
    destination: Destination
    start_date: datetime
    end_date: datetime
    cost: float
    travelers: List[str]
    observations: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TripPublic(TripBase):
    id: str
    created_at: datetime
    updated_at: datetime


class TripsPublic(BaseModel):
    data: List[TripPublic]
    page: int
    next: Optional[str]


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    name: Optional[str]
    destination: Optional[Destination]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    cost: Optional[float]
    travelers: Optional[List[str]]
    observations: Optional[Dict[str, Any]]
