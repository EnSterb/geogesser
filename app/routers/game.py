# app/game.py
import math
import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import JSON, select
from app.models import Location, User, Room, RoomRound, SoloRoom, SoloRound
from app.routers.auth import oauth2_scheme
from app.schemas import LocationPublic, SoloRoomCreate
from sqlalchemy.orm import Session
import random
from app.database import get_db
from load_to_database import locations
from app.utils import get_location_json
from fastapi import Request
load_dotenv()

router = APIRouter(
    prefix="/game",
    tags=["Game"],
)


# Маршрут для старта одиночной игры и получения случайных локаций
@router.get("/locations", response_model=list[dict])
def get_locations(num_locations: int = Query(3, ge=1, le=50)):
    """
    Возвращает указанное количество локаций в формате JSON.

    Параметры:
    - num_locations: количество локаций для игры (по умолчанию 3).

    Если в базе недостаточно локаций, вернётся ошибка 404.
    """
    db = next(get_db())
    try:
        locations_result = []
        for i in range(1, num_locations+1):
            while True:
                loc = get_location_json()
                if loc not in locations_result:
                    locations_result.append(loc)
                    break
        return locations_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


def get_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None  # Если токен отсутствует, возвращаем None

    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        user_id = int(payload.get("sub"))
    except (jwt.JWTError, ValueError):
        return None  # Ошибка при декодировании токена, возвращаем None

    user = db.query(User).filter(User.id_user == user_id).first()
    return user  # Возвращаем пользователя, если он найден

# Роут для создания комнаты
@router.post("/create-solo-room")
def create_solo_room(
    data: SoloRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_cookie)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Логика для создания комнаты
    location_ids = db.query(Location.id_location).all()
    location_ids = [loc[0] for loc in location_ids]

    if len(location_ids) < data.rounds:
        raise HTTPException(status_code=400, detail="Not enough locations in database")

    chosen_ids = random.sample(location_ids, data.rounds)

    room = SoloRoom(id_user=current_user.id_user, total_rounds = data.rounds)
    db.add(room)
    db.commit()
    db.refresh(room)

    for i, id_loc in enumerate(chosen_ids, start=1):
        round_entry = SoloRound(
            id_solo_room=room.id_solo_room,
            round_number=i,
            id_location=id_loc
        )
        db.add(round_entry)

    db.commit()

    return {"room_id": room.id_solo_room}


@router.get("/room/{id_solo_room}")
def get_room_by_id(id_solo_room: int, db: Session = Depends(get_db)):
    # Находим комнату по id_solo_room
    room = db.query(SoloRoom).filter(SoloRoom.id_solo_room == id_solo_room).first()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    # Находим раунды этой комнаты
    rounds = db.query(SoloRound).filter(SoloRound.id_solo_room == room.id_solo_room).all()

    # Возвращаем информацию о комнате и раундах
    return {
        "room_id": room.id_solo_room,
        "created_at": room.created_at.strftime("%d.%m.%Y %H:%M"),
        "rounds": [
            {"round_number": round_entry.round_number, "location_id": round_entry.id_location}
            for round_entry in rounds
        ]
    }

def haversine(lat1, lon1, lat2, lon2):
    # Расстояние между двумя координатами (в метрах)
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class EndRoundRequest(BaseModel):
    room_id: int
    guessed_lat: float
    guessed_lng: float

def calculate_score(distance_meters):
    """
    Мягкий спад очков при увеличении расстояния.
    """
    distance_km = distance_meters / 1000
    score = 5000 * math.exp(-distance_km / 15)  # Меньше спад
    return int(score)

@router.post("/single-game/end-round")
def end_round(data: EndRoundRequest, db: Session = Depends(get_db)):
    room = db.query(SoloRoom).filter(SoloRoom.id_solo_room == data.room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Проверка, что пользователь имеет доступ к комнате
    current_user = db.query(User).filter(User.id_user == room.id_user).first()
    if current_user.id_user != db.execute(select(SoloRoom.id_user).where(SoloRoom.id_solo_room == data.room_id)).scalar():
        raise HTTPException(status_code=403, detail="You do not have access to this room")

    current_round_number = room.current_round_number
    round = db.query(SoloRound).filter_by(id_solo_room=room.id_solo_room, round_number=current_round_number).first()

    if not round:
        raise HTTPException(status_code=404, detail="Round not found")

    location = round.location
    distance = haversine(location.latitude, location.longitude, data.guessed_lat, data.guessed_lng)

    # Вычисляем очки — чем ближе, тем выше (например, максимум 5000 за 0 м)
    score = calculate_score(distance_meters=distance)

    # Добавим очки пользователю
    user = db.query(User).filter(User.id_user == room.id_user).first()
    user.solo_score += score
    room.total_score += score
    # Переход к следующему раунду
    if current_round_number == room.total_rounds:
        # Если это последний раунд, удаляем все раунды, комнату и пользователя
        db.query(SoloRound).filter(SoloRound.id_solo_room == room.id_solo_room).delete()
        db.delete(room)
        db.commit()
    if current_round_number != room.total_rounds:
        room.current_round_number += 1
        db.commit()
    left_rounds = room.total_rounds-current_round_number
    return {
        "left_rounds": left_rounds,
        "score": score,
        "distance": distance,
        "location": {
            "lat": location.latitude,
            "lng": location.longitude
        },
        "total_score": room.total_score if left_rounds == 0 else None
    }
