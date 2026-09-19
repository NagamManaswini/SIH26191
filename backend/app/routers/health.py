from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.database import get_db
from backend.app.schemas.common import HealthResponse
from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify backend service and database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable ({str(e)})"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        database_status=db_status,
        app_name=settings.APP_NAME,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/db-test")
@router.get("/api/v1/db-test", include_in_schema=False)
def db_test(db: Session = Depends(get_db)):
    """Simple database health verification endpoint."""
    try:
        result = db.execute(text("SELECT current_database()")).scalar()
        return {
            "status": "connected",
            "database": str(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }

