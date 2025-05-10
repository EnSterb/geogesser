import pandas as pd
from app.database import SessionLocal
from app.models import Location

# Загрузка CSV
df = pd.read_csv("coordinates_image.csv", encoding="utf-8")

# Создаём сессию
# session = SessionLocal()

locations = [
    Location(id_image=row.id_image, latitude=row.latitude, longitude=row.longitude)
    for row in df.itertuples(index=False)
]

# Добавляем в базу
# session.add_all(locations)
# session.commit()

# Закрываем сессию
# session.close()
# print(df.head())