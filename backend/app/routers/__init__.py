from backend.app.routers.health import router as health_router
from backend.app.routers.shelters import router as shelters_router
from backend.app.routers.hazard_zones import router as hazard_zones_router
from backend.app.routers.population import router as population_router
from backend.app.routers.rainfall import router as rainfall_router
from backend.app.routers.risk import router as risk_router
from backend.app.routers.routes import router as routes_router
from backend.app.routers.relocation import router as relocation_router
from backend.app.routers.simulation import router as simulation_router
from backend.app.routers.alerts import router as alerts_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.demo import router as demo_router
from backend.app.routers.ai_assistant import router as ai_assistant_router
from backend.app.routers.animals import router as animals_router
from backend.app.routers.communications import router as communications_router
from backend.app.routers.weather import router as weather_router
from backend.app.routers.reports import router as reports_router
from backend.app.routers.hospitals import router as hospitals_router
from backend.app.routers.hospital_portal import router as hospital_portal_router

__all__ = [
    "health_router",
    "shelters_router",
    "hazard_zones_router",
    "population_router",
    "rainfall_router",
    "risk_router",
    "routes_router",
    "relocation_router",
    "simulation_router",
    "alerts_router",
    "auth_router",
    "demo_router",
    "ai_assistant_router",
    "animals_router",
    "communications_router",
    "weather_router",
    "reports_router",
    "hospitals_router",
    "hospital_portal_router",
]
