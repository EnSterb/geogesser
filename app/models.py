from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, BigInteger
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

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
