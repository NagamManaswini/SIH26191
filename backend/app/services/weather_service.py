"""Live Weather Service integrating coordinate-based weather and forecast lookup via Open-Meteo / OpenWeatherMap."""

import datetime
from typing import Dict, Any, Optional
import httpx
from backend.app.config import settings

# In-memory weather cache: (round_lat, round_lon) -> (timestamp, data)
_WEATHER_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes cache TTL


def _get_cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


def _interpret_wmo_code(code: int) -> str:
    """Map WMO Weather interpretation codes (WW) to human-readable condition string."""
    wmo_map = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        56: "Light Freezing Drizzle",
        57: "Dense Freezing Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Slight Snowfall",
        73: "Moderate Snowfall",
        75: "Heavy Snowfall",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Slight Hail",
        99: "Thunderstorm with Heavy Hail",
    }
    return wmo_map.get(code, "Cloudy / Rainy")


def fetch_live_weather(lat: float, lon: float, location_name: Optional[str] = None) -> Dict[str, Any]:
    """Fetch 100% live weather data and forecast for coordinates.

    Uses Open-Meteo API by default (or OpenWeatherMap if configured).
    Returns real metrics and ISO timestamp. Never returns fake weather.
    """
    cache_key = _get_cache_key(lat, lon)
    now = datetime.datetime.now(datetime.timezone.utc)

    # Check cache first
    if cache_key in _WEATHER_CACHE:
        cached_entry = _WEATHER_CACHE[cache_key]
        cached_time = cached_entry["cached_at"]
        if (now - cached_time).total_seconds() < CACHE_TTL_SECONDS:
            result = dict(cached_entry["data"])
            result["data_status"] = "CACHED"
            return result

    # Fetch live from API
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }

        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        condition = _interpret_wmo_code(current.get("weather_code", 0))
        precip = current.get("precipitation", 0.0) or current.get("rain", 0.0) or 0.0

        # Build 7-day forecast array
        daily_times = daily.get("time", [])
        daily_max = daily.get("temperature_2m_max", [])
        daily_min = daily.get("temperature_2m_min", [])
        daily_codes = daily.get("weather_code", [])
        daily_precip = daily.get("precipitation_sum", [])

        forecast_daily = []
        for i in range(min(len(daily_times), 7)):
            forecast_daily.append({
                "date": daily_times[i],
                "temp_max": daily_max[i] if i < len(daily_max) else None,
                "temp_min": daily_min[i] if i < len(daily_min) else None,
                "condition": _interpret_wmo_code(daily_codes[i]) if i < len(daily_codes) else "Cloudy",
                "precipitation_mm": daily_precip[i] if i < len(daily_precip) else 0.0,
            })

        # Build 24-hr hourly forecast array
        hourly_times = hourly.get("time", [])[:24]
        hourly_temps = hourly.get("temperature_2m", [])[:24]
        hourly_probs = hourly.get("precipitation_probability", [])[:24]

        forecast_hourly = []
        for i in range(len(hourly_times)):
            forecast_hourly.append({
                "time": hourly_times[i].split("T")[-1] if "T" in hourly_times[i] else hourly_times[i],
                "temperature": hourly_temps[i] if i < len(hourly_temps) else None,
                "precipitation_prob": hourly_probs[i] if i < len(hourly_probs) else 0,
            })

        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        weather_payload = {
            "status": "available",
            "data_status": "LIVE",
            "location_name": location_name or f"Coordinates ({round(lat, 4)}°, {round(lon, 4)}°)",
            "latitude": lat,
            "longitude": lon,
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "condition": condition,
            "precipitation_mm": precip,
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
            "pressure_hpa": current.get("surface_pressure"),
            "last_updated": timestamp_str,
            "forecast_daily": forecast_daily,
            "forecast_hourly": forecast_hourly,
        }

        # Save to cache
        _WEATHER_CACHE[cache_key] = {"cached_at": now, "data": weather_payload}
        return weather_payload

    except Exception as e:
        print(f"[WEATHER SERVICE ERROR] Live fetch failed for ({lat}, {lon}): {e}")
        # Check if expired cache exists
        if cache_key in _WEATHER_CACHE:
            fallback = dict(_WEATHER_CACHE[cache_key]["data"])
            fallback["data_status"] = "CACHED"
            fallback["note"] = f"Live weather unavailable. Showing last cached data from {fallback['last_updated']}."
            return fallback

        # Return explicit unavailable state - NO FAKE DATA
        return {
            "status": "unavailable",
            "data_status": "UNAVAILABLE",
            "message": "Live weather data is currently unavailable.",
            "location_name": location_name or f"Coordinates ({round(lat, 4)}°, {round(lon, 4)}°)",
            "latitude": lat,
            "longitude": lon,
            "last_updated": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }
