import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db, engine

router = APIRouter(tags=["Health"])

class HealthCheckResponse(BaseModel):
    status: str
    service: str

class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    dialect: str
    latency_ms: float
    message: str

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Core backend service health check.
    """
    return {
        "status": "ok",
        "service": "flash-flood-backend"
    }

@router.get("/health/db", response_model=DatabaseHealthResponse)
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database connection and query responsiveness health check.
    """
    start_time = time.perf_counter()
    try:
        # Execute lightweight ping query
        result = db.execute(text("SELECT 1")).scalar()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        dialect_name = engine.dialect.name
        
        if result == 1:
            return {
                "status": "ok",
                "database": "connected",
                "dialect": dialect_name,
                "latency_ms": latency_ms,
                "message": f"Successfully connected to {dialect_name} database"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database ping query did not return expected result"
            )
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "database": "disconnected",
                "dialect": engine.dialect.name,
                "latency_ms": latency_ms,
                "error": str(e)
            }
        )
