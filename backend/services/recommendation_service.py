from backend.models import Station
from utils.distance import calculate_distance
from sqlalchemy.orm import Session

def get_recommended_stations(db: Session, user_lat: float, user_lng: float, max_distance_km: float = 20.0):
    stations = db.query(Station).filter(Station.is_active == True).all()
    
    recommendations = []
    for station in stations:
        dist = calculate_distance(user_lat, user_lng, station.location_lat, station.location_lng)
        if dist <= max_distance_km:
            recommendations.append({
                "station": station,
                "distance": dist
            })
            
    # Sort by distance first, then by price (simplified recommendation engine)
    recommendations.sort(key=lambda x: (x["distance"], x["station"].price_per_hour))
    
    return recommendations
