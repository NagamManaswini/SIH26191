import sys
import os

# Configure sys.path so imports work regardless of deployment entrypoint (root or backend)
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_backend_dir)
for _p in [_root_dir, _backend_dir, _current_dir]:
    if _p and os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import (
    health_router,
    shelters_router,
    hazard_zones_router,
    population_router,
    rainfall_router,
    risk_router,
    routes_router,
    relocation_router,
    simulation_router,
    alerts_router,
    auth_router,
    demo_router,
    ai_assistant_router,
    animals_router,
    communications_router,
    weather_router,
    reports_router,
    hospitals_router,
    hospital_portal_router,
)


# API Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for setup and teardown tasks."""
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization error: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="API for Intelligent Hazard Red Zone Mapping, Carrying Capacity Assessment & Relocation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )


# Register Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(shelters_router, prefix=settings.API_V1_STR)
app.include_router(hazard_zones_router, prefix=settings.API_V1_STR)
app.include_router(hazard_zones_router, prefix="/api/v1/hazard-zones", tags=["Hazard Zones"], include_in_schema=False)
app.include_router(population_router, prefix=settings.API_V1_STR)
app.include_router(rainfall_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(routes_router, prefix=settings.API_V1_STR)
app.include_router(relocation_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)
app.include_router(ai_assistant_router, prefix=settings.API_V1_STR)
app.include_router(animals_router, prefix=settings.API_V1_STR)
app.include_router(communications_router, prefix=settings.API_V1_STR)
app.include_router(weather_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(hospitals_router, prefix=settings.API_V1_STR)
app.include_router(hospital_portal_router, prefix=settings.API_V1_STR)



from fastapi.staticfiles import StaticFiles

# Serve frontend production bundle if built (for all-in-one offline field deployment)
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    # Mount assets folder
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/manifest.json")
    def serve_manifest():
        manifest_path = os.path.join(frontend_dist, "manifest.json")
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/manifest+json")
        return JSONResponse(status_code=404, content={"detail": "manifest.json not found"})

    @app.get("/sw.js")
    def serve_sw():
        sw_path = os.path.join(frontend_dist, "sw.js")
        if os.path.exists(sw_path):
            return FileResponse(sw_path, media_type="application/javascript")
        return JSONResponse(status_code=404, content={"detail": "sw.js not found"})

    @app.get("/")
    def serve_frontend_root():
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "documentation": "/docs",
            "health_check": "/health",
        }
else:
    @app.get("/")
    def root():
        """Root endpoint redirecting info to docs."""
        return {
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "documentation": "/docs",
            "health_check": "/health",
            "pdf_download": "/download-pdf",
        }


@app.get("/download-pdf")
def download_pdf():
    """Endpoint to download the project overview & workflow PDF report."""
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Disaster_Management_Platform_All_Features_Guide.pdf")
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Disaster_Platform_Detailed_Overview_and_Workflows.pdf")
    
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path),
        )
    return JSONResponse(status_code=404, content={"detail": "PDF report file not found."})


@app.get("/download-features-pdf")
def download_features_pdf():
    """Endpoint to download the complete all-features guide PDF."""
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Disaster_Management_Platform_All_Features_Guide.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="Disaster_Management_Platform_All_Features_Guide.pdf",
        )
    return JSONResponse(status_code=404, content={"detail": "Features PDF report file not found."})


