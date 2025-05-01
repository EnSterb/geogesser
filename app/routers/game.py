# app/game.py
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import JSON
from app.models import Location
from app.schemas import LocationPublic
from sqlalchemy.orm import Session
import random
from app.database import get_db
from load_to_database import locations
from app.utils import get_location_json

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