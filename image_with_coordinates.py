import requests
import csv
import time
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
OUTPUT_FILE = "coordinates_image.csv"

# Задай границы всей карты (например, Париж)
MIN_LAT = 48.80
MAX_LAT = 48.90
MIN_LON = 2.25
MAX_LON = 2.45
STEP = 0.01  # Размер клетки (0.01 = ~1.1 км)

FIELDS = "id,geometry"
LIMIT = 2000


def fetch_images(bbox):
    url = "https://graph.mapillary.com/images"
    params = {
        "access_token": ACCESS_TOKEN,
        "bbox": bbox,
        "fields": FIELDS,
        "is_pano": "true",
        "limit": LIMIT
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def generate_grid(min_lat, max_lat, min_lon, max_lon, step):
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            yield round(lon, 5), round(lat, 5), round(lon + step, 5), round(lat + step, 5)
            lon += step
        lat += step


def main():
    all_results = []

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(["image_id", "lat", "lon"])  # Убираем если не нужно

        for bbox in tqdm(generate_grid(MIN_LAT, MAX_LAT, MIN_LON, MAX_LON, STEP), desc="Обработка сетки"):
            bbox_str = ",".join(map(str, bbox))
            images = fetch_images(bbox_str)

            for img in images:
                image_id = img["id"]
                coords = img["geometry"]["coordinates"]  # [lon, lat]
                lon, lat = coords
                writer.writerow([image_id, lat, lon])

            time.sleep(0.3)  # чтобы не попасть под rate limit

    print(f"\n✅ Готово! Сохранено в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
