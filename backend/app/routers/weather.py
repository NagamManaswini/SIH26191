"""FastAPI Router for Live Coordinate-Based Weather Data & Forecast."""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from backend.app.services.weather_service import fetch_live_weather

router = APIRouter(prefix="/weather", tags=["Live Weather Engine"])


@router.get("/live", summary="Get live weather for exact coordinates")
def get_live_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    location_name: Optional[str] = Query(None, description="Optional human-readable location name"),
):
    """Retrieve 100% live weather data and 5-7 day forecast for any coordinates across India and globally."""
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates. Latitude must be in [-90, 90] and Longitude in [-180, 180].",
        )

    return fetch_live_weather(lat, lon, location_name)
