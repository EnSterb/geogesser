from geopy.distance import geodesic
from app.database import get_location
import random
import os
from dotenv import load_dotenv

load_dotenv()

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers

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
