from .health import router as health_router
from .overview import router as overview_router
from .sensors import router as sensors_router
from .watersheds import router as watersheds_router
from .auth import router as auth_router
from .rbac_demo import router as rbac_router

__all__ = [
    "health_router",
    "overview_router",
    "sensors_router",
    "watersheds_router",
    "auth_router",
    "rbac_router",
]
