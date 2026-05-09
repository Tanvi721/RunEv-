from sqlalchemy.orm import Session
from backend.models import Station, Slot

def get_all_stations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Station).filter(Station.is_active == True).offset(skip).limit(limit).all()

def get_station_by_id(db: Session, station_id: int):
    return db.query(Station).filter(Station.id == station_id).first()

def get_slots_for_station(db: Session, station_id: int):
    return db.query(Slot).filter(Slot.station_id == station_id).all()
