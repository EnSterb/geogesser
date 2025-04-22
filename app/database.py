from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from fastapi import Depends
from sqlalchemy.orm import Session

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123123123@localhost:3306/geogesser"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
