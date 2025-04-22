from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers

# distance = calculate_distance(55.7558, 37.6173, 59.9343, 30.3351)
# print(f"Расстояние: {distance:.2f} км")
# print(type(distance))


