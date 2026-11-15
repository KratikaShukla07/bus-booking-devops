from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date
from typing import Literal

class Passenger(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

class BookingCreate(BaseModel):
    trip_id: int
    seat_no: int = Field(ge=1)
    travel_date: date
    boarding_stop: str
    drop_stop: str
    passenger: Passenger

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pnr: str
    trip_id: int
    seat_no: int
    passenger_name: str
    passenger_email: str
    boarding_stop: str
    drop_stop: str
    status: str
