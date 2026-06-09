from pydantic import BaseModel
from datetime import date, time

class UserAuth(BaseModel):
    username: str
    password: str

class BookingCreate(BaseModel):
    room: str
    booking_date: date
    start_time: time
    end_time: time

class BookingResponse(BaseModel):
    id: str
    room: str
    username: str
    booking_date: date
    start_time: time
    end_time: time