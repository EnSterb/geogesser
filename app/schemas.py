from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime


# --- AUTH --- #
class UserCreate(BaseModel):
    nickname: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    user_id: int
    email: Optional[str] = None


class UserPublic(BaseModel):
    id: int
    nickname: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# --- LOCATION --- #
class LocationPublic(BaseModel):
    id: int
    name: str
    image_url: str

    class Config:
        from_attributes = True


class LocationFull(LocationPublic):
    latitude: float
    longitude: float


# --- ROOM --- #
class CreateRoom(BaseModel):
    host_id: int  # можно заменить на nickname/email если токен не используешь


class JoinRoom(BaseModel):
    room_code: str
    guest_id: int


class RoomInfo(BaseModel):
    code: str
    host_id: int
    guest_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- ROUND --- #
class GuessSubmission(BaseModel):
    round_id: int
    lat: float
    lon: float
    player: Literal["host", "guest"]


class GuessResult(BaseModel):
    distance_km: float
    correct_lat: float
    correct_lon: float


class RoomRoundPublic(BaseModel):
    id: int
    location: LocationPublic
    host_guess_lat: Optional[float]
    host_guess_lon: Optional[float]
    guest_guess_lat: Optional[float]
    guest_guess_lon: Optional[float]
    host_distance_km: Optional[float]
    guest_distance_km: Optional[float]

    class Config:
        from_attributes = True
