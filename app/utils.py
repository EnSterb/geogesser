from typing import Optional
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from geopy.distance import geodesic
from jose import jwt, JWTError
from passlib.context import CryptContext
from requests import Request

from app.database import get_location
import random
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками по координатам.
    Вход: широты и долготы двух точек.
    Возвращает расстояние в километрах.
    """
    R = 6371  # Радиус Земли в километрах

    # Преобразование градусов в радианы
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Разница координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Формула гаверсинуса
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


# distance = calculate_distance(55.7558, 37.6173, 59.9343, 30.3351)
# print(f"Расстояние: {distance:.2f} км")
# print(type(distance))

def get_location_json():
    count_location = os.getenv('COUNT_LOCATION')
    location = {}
    loc = get_location(random.randint(1, int(count_location)))
    location['id_image'] = loc.id_image
    location['latitude'] = loc.latitude
    location['longitude'] = loc.longitude

    return location

# print(get_location_json())
def hash_password(password:Optional[str]) -> Optional[str]:
    return pwd_context.hash(password)

def verify_password(plain_password:Optional[str], hashed_password: Optional[str]) -> Optional[bool]:
    return pwd_context.verify(plain_password, hashed_password)

def verify_token_validity(token: str, BASE_URL: str = os.getenv("BASE_URL")):
    me_url = f"{BASE_URL}/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(me_url, headers=headers)

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Токен истек или недействителен.")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Неизвестная ошибка при проверке токена.")
    return response.json()
