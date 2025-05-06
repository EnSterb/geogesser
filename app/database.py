import os
from typing import Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Location

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_location(id_location):
    stmt = select(Location).where(Location.id_location == id_location)
    result = Session(bind=engine).execute(stmt).scalar_one()
    return result

def user_exists(email:Optional[str]) -> bool:
    db = next(get_db())
    try:
        return db.query(User).filter(User.email == email).first() is not None
    finally:
        db.close()