# app/game.py
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import Location
from app.schemas import LocationPublic
from sqlalchemy.orm import Session
import random
from app.database import get_db

router = APIRouter()


# Маршрут для старта одиночной игры и получения случайных локаций
@router.get("/single/start", response_model=list[LocationPublic])
def start_game(num_locations: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    """
    Старт игры для одного игрока с указанным количеством случайных локаций.
    По умолчанию возвращается 5 локаций, но можно указать больше или меньше.

    Параметры:
    - num_locations: количество локаций для игры (по умолчанию 5).

    Если в базе недостаточно локаций, вернётся ошибка 404.
    """

    # Получаем все локации из базы данных
    locations = db.query(Location).all()

    # Если в базе данных меньше локаций, чем запрашивает игрок, возвращаем ошибку
    if 0 < len(locations) < num_locations:
        raise HTTPException(status_code=404, detail="Location Error")

    # Выбираем случайные локации (не повторяющиеся)
    selected_locations = random.sample(locations, num_locations)

    return selected_locations
