import sqlite3
import uuid
from datetime import date, time
from fastapi import APIRouter, HTTPException, Header
from typing import List
from schemas import BookingCreate, BookingResponse
from config import DB_FILE

router = APIRouter(tags=["Bookings"])

@router.get("/api/bookings/{room}", response_model=List[BookingResponse])
def get_bookings(room: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, room, username, booking_date, start_time, end_time FROM bookings WHERE room = ?", (room,))
        rows = cursor.fetchall()
        return [{
            "id": r[0], "room": r[1], "username": r[2],
            "booking_date": date.fromisoformat(r[3]),
            "start_time": time.fromisoformat(r[4]),
            "end_time": time.fromisoformat(r[5])
        } for r in rows]

@router.post("/api/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, x_token: str = Header(...)):
    if booking.start_time >= booking.end_time:
        raise HTTPException(status_code=400, detail="Время окончания должно быть позже начала")

    b_date, b_start, b_end = booking.booking_date.isoformat(), booking.start_time.isoformat(), booking.end_time.isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT start_time, end_time FROM bookings WHERE room = ? AND booking_date = ?", (booking.room, b_date))
        for ex_start, ex_end in cursor.fetchall():
            if not (b_end <= ex_start or b_start >= ex_end):
                raise HTTPException(status_code=400, detail="Это время уже занято")
        
        booking_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?)", (booking_id, booking.room, x_token, b_date, b_start, b_end))
        conn.commit()

    return {
        "id": booking_id,
        "room": booking.room,
        "username": x_token,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time
    }

@router.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: str, x_token: str = Header(...)):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE username = ?", (x_token,))
        user_row = cursor.fetchone()
        is_admin = user_row[0] if user_row else 0

        cursor.execute("SELECT username FROM bookings WHERE id = ?", (booking_id,))
        booking_row = cursor.fetchone()
        if not booking_row:
            raise HTTPException(status_code=404, detail="Бронь не найдена")

        if booking_row[0] != x_token and not is_admin:
            raise HTTPException(status_code=403, detail="Вы не можете удалить чужую бронь")

        cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
    return {"message": "Бронь удалена"}