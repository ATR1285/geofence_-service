from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

app = FastAPI(title="Geofence Event Processing Service")

class LocationEvent(BaseModel):
    vehicle_id: str = Field(..., example="TAXI_001")
    lat: float = Field(..., example=12.9716)
    lon: float = Field(..., example=77.5946)
    timestamp: datetime = Field(..., example="2025-11-30T12:30:00Z")


class ZoneChangeEvent(BaseModel):
    vehicle_id: str
    previous_zone: Optional[str]
    current_zone: Optional[str]
    entered_zone: Optional[str]
    exited_zone: Optional[str]
    timestamp: datetime


class VehicleStatus(BaseModel):
    vehicle_id: str
    current_zone: Optional[str]
    last_update: Optional[datetime]


class Zone(BaseModel):
    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float



ZONES = [
    Zone(name="AIRPORT", min_lat=12.94, max_lat=13.00, min_lon=77.60, max_lon=77.70),
    Zone(name="DOWNTOWN", min_lat=12.95, max_lat=13.05, min_lon=77.55, max_lon=77.65),
    Zone(name="SUBURB", min_lat=12.85, max_lat=12.95, min_lon=77.50, max_lon=77.60),
]


def get_zone_for_point(lat: float, lon: float) -> Optional[str]:
    for zone in ZONES:
        if zone.min_lat <= lat <= zone.max_lat and zone.min_lon <= lon <= zone.max_lon:
            return zone.name
    return None




class VehicleState(BaseModel):
    current_zone: Optional[str]
    last_update: Optional[datetime]


vehicle_states: Dict[str, VehicleState] = {}




@app.post("/events", response_model=ZoneChangeEvent)
def ingest_event(event: LocationEvent):
    new_zone = get_zone_for_point(event.lat, event.lon)
    state = vehicle_states.get(event.vehicle_id, VehicleState(current_zone=None, last_update=None))
    previous_zone = state.current_zone

    entered_zone = None
    exited_zone = None

    if previous_zone != new_zone:
        if previous_zone is not None:
            exited_zone = previous_zone
        if new_zone is not None:
            entered_zone = new_zone

    state.current_zone = new_zone
    state.last_update = event.timestamp
    vehicle_states[event.vehicle_id] = state

    return ZoneChangeEvent(
        vehicle_id=event.vehicle_id,
        previous_zone=previous_zone,
        current_zone=new_zone,
        entered_zone=entered_zone,
        exited_zone=exited_zone,
        timestamp=event.timestamp,
    )


@app.get("/vehicles/{vehicle_id}/status", response_model=VehicleStatus)
def get_vehicle_status(vehicle_id: str):
    state = vehicle_states.get(vehicle_id)
    if not state:
        return VehicleStatus(vehicle_id=vehicle_id, current_zone=None, last_update=None)

    return VehicleStatus(
        vehicle_id=vehicle_id,
        current_zone=state.current_zone,
        last_update=state.last_update,
    )
@app.get("/")
def root():
    return {"message": "Geofence API is running. Visit /docs for API testing."}
