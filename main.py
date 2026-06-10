from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db import init_db
from routers.auth import router as auth_router
from routers.rooms import router as rooms_router
from routers.bookings import router as bookings_router
from routers.users import router as users_router# добавила

app = FastAPI(title="Сервис бронирования переговорных")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(users_router)# добавила

# Монтирование фронтенда
#app.mount("/", StaticFiles(directory="../frontend/", html=True), name="frontend") #изначально было так
# все что ниже я добавила для запуска в пайчарме
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8080, reload=True)
