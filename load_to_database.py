import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal  # или как у тебя называется сессия
from app.models import Location        # путь до модели

# Загрузка CSV
df = pd.read_csv("coordinates_image.csv", encoding="utf-8")

# Создаём сессию
session = SessionLocal()

locations = [
    Location(id_image=row.id_image, latitude=row.latitude, longitude=row.longitude)
    for row in df.itertuples(index=False)
]

# Добавляем в базу
session.add_all(locations)
session.commit()

# Закрываем сессию
session.close()
# print(df.head())