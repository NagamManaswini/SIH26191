from .health import router as health_router
from .shelters import router as shelters_router
from .hazard_zones import router as hazard_zones_router
from .population import router as population_router
from .rainfall import router as rainfall_router
from .risk import router as risk_router
from .routes import router as routes_router
from .relocation import router as relocation_router
from .simulation import router as simulation_router
from .alerts import router as alerts_router
from .auth import router as auth_router
from .demo import router as demo_router
from .ai_assistant import router as ai_assistant_router
from .animals import router as animals_router
from .communications import router as communications_router
from .weather import router as weather_router
from .reports import router as reports_router
from .hospitals import router as hospitals_router
from .hospital_portal import router as hospital_portal_router

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
