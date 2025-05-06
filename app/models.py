from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, BigInteger, text
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    solo_score: Mapped[int] = mapped_column(Integer, default=0)
    multi_score: Mapped[int] = mapped_column(Integer, default=0)

    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")


class Location(Base):
    __tablename__ = 'locations'

    id_location: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_image: Mapped[int] = mapped_column(BigInteger)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

class Room(Base):
    __tablename__ = 'rooms'

    id_room: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id_user"))
    guest_id: Mapped[int | None] = mapped_column(ForeignKey("users.id_user"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    rounds: Mapped[list["RoomRound"]] = relationship(back_populates="room")

class RoomRound(Base):
    __tablename__ = 'room_rounds'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id_room"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id_location"))

    host_guess_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    host_guess_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    guest_guess_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    guest_guess_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    host_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    guest_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    room: Mapped["Room"] = relationship(back_populates="rounds")
    location: Mapped["Location"] = relationship()

class PasswordResetToken(Base):
    __tablename__ = "password_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id_user"))
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user = relationship("User", back_populates="password_reset_tokens")

class TempUsers(Base):
    __tablename__ = "temp_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

class GameRoom(Base):
    __tablename__ = "game_rooms"
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    current_round = Column(Integer, default=1)
    total_score = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id_user"), nullable=True)

class SoloRoom(Base):
    __tablename__ = 'solo_rooms'

    id_solo_room: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id_user"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_finished: Mapped[bool] = mapped_column(default=False)

    rounds = relationship("SoloRound", back_populates="room")


class SoloRound(Base):
    __tablename__ = 'solo_rounds'

    id_solo_round: Mapped[int] = mapped_column(primary_key=True)
    id_solo_room: Mapped[int] = mapped_column(ForeignKey("solo_rooms.id_solo_room"))
    round_number: Mapped[int]
    id_location: Mapped[int] = mapped_column(ForeignKey("locations.id_location"))

    room = relationship("SoloRoom", back_populates="rounds")
