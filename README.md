# Geofence Event Processing Service

This project implements a simple geofence processing web service using FastAPI.

## Features
- Accepts vehicle GPS events via REST API.
- Detects when a vehicle enters or exits predefined zones.
- Stores and retrieves current zone status of vehicles.

## Tech Stack
- Python 3
- FastAPI
- Uvicorn
- Pydantic

## Assumptions
- Zones are rectangular.
- Only one zone is active per vehicle at a time.
- System uses in-memory storage for simplicity.

## API Endpoints

### POST /events
Accepts vehicle GPS data and returns zone entry/exit details.

### GET /vehicles/{vehicle_id}/status
Returns the current zone and last update timestamp of a vehicle.

## How to Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
