from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.overview import router as overview_router
from app.routers.sensors import router as sensors_router
from app.routers.watersheds import router as watersheds_router
from app.routers.auth import router as auth_router
from app.routers.rbac_demo import router as rbac_router
from app.routers.map import router as map_router
from app.routers.risk import router as risk_router
from app.routers.predictions import router as predictions_router
from app.routers.alerts import router as alerts_router
from app.routers.citizen_reports import router as citizen_reports_router
from app.routers.evacuation import router as evacuation_router
from app.routers.command_center import router as command_center_router
from app.routers.edge import router as edge_router
from app.routers.analytics import router as analytics_router
from app.routers.demo import router as demo_router
from app.websocket.manager import ws_manager
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flash_flood_api")

# Ensure all database tables are created on startup if using direct SQLite or testing
Base.metadata.create_all(bind=engine)

# Ensure new columns on existing SQLite tables are present
with engine.connect() as conn:
    for tbl, col, col_type, default_val in [
        ("watersheds", "average_slope_deg", "FLOAT", "24.5"),
        ("watersheds", "elevation_m", "FLOAT", "1850.0"),
        ("citizen_reports", "confidence_score", "FLOAT", "50.0"),
        ("citizen_reports", "verified_by_user_id", "INTEGER", "NULL"),
        ("citizen_reports", "verified_at", "DATETIME", "NULL"),
        ("citizen_reports", "verification_notes", "TEXT", "NULL"),
        ("evacuation_centers", "is_active", "BOOLEAN", "1"),
        ("evacuation_centers", "district", "VARCHAR(100)", "'Rudraprayag'"),
        ("evacuation_centers", "elevation_m", "FLOAT", "2100.0"),
    ]:
        try:
            conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN {col} {col_type} DEFAULT {default_val}"))
            conn.commit()
        except Exception:
            pass

# Seed default demo users for seamless login
try:
    with SessionLocal() as db_session:
        demo_seed_list = [
            ("Admin Disaster Operations", "admin@disaster.gov.in", "AdminPass123!", UserRole.ADMIN, "+91-9876543201"),
            ("Citizen Volunteer", "citizen@disaster.gov.in", "CitizenPass123!", UserRole.CITIZEN, "+91-9876543202"),
            ("NDRF Field Ops Commander", "responder@disaster.gov.in", "ResponderPass123!", UserRole.RESPONSE_TEAM, "+91-9876543203"),
            ("Disaster Relief Officer", "official@disaster.gov.in", "OfficialPass123!", UserRole.GOVERNMENT_OFFICIAL, "+91-9876543204"),
            ("Admin Flash Flood", "admin@flashflood.gov.in", "password123", UserRole.ADMIN, "+91-9876543205"),
            ("District Officer Sharma", "officer.sharma@disastermgmt.gov.in", "password123", UserRole.GOVERNMENT_OFFICIAL, "+91-9876543206"),
            ("Commander NDRF", "commander.ndrf@response.gov.in", "password123", UserRole.RESPONSE_TEAM, "+91-9876543207"),
            ("Dr. Anita Hydrology", "dr.anita.hydrology@research.ac.in", "password123", UserRole.RESEARCHER, "+91-9876543208"),
            ("Volunteer Sonprayag", "volunteer.sonprayag@community.in", "password123", UserRole.CITIZEN, "+91-9876543209"),
        ]
        for name, email, password, role, phone in demo_seed_list:
            existing = db_session.query(User).filter(User.email == email).first()
            if not existing:
                db_session.add(User(
                    name=name,
                    email=email,
                    password_hash=get_password_hash(password),
                    role=role,
                    phone=phone,
                    district="Rudraprayag",
                    state="Uttarakhand"
                ))
            else:
                existing.password_hash = get_password_hash(password)
        db_session.commit()
except Exception as e:
    logger.warning(f"Default user seeding notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Hyper-local real-time flash flood forecasting and early-warning platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(overview_router, prefix=settings.API_V1_STR)
app.include_router(sensors_router, prefix=settings.API_V1_STR)
app.include_router(watersheds_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(rbac_router, prefix=settings.API_V1_STR)
app.include_router(map_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(citizen_reports_router, prefix=settings.API_V1_STR)
app.include_router(evacuation_router, prefix=settings.API_V1_STR)
app.include_router(command_center_router, prefix=settings.API_V1_STR)
app.include_router(edge_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to SIH26192 Flash Flood Early Warning API",
        "health_check": f"{settings.API_V1_STR}/health",
        "db_health_check": f"{settings.API_V1_STR}/health/db",
        "auth_docs": f"{settings.API_V1_STR}/auth",
        "documentation": "/docs"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"event": "ack", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/sensors")
async def websocket_sensors_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"event": "ack", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"event": "ack", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

