from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_engine import AnalyticsEngine
from app.schemas.analytics import AnalyticsSummaryKPIs, AnalyticsChartsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Historical Flood Analysis"])

@router.get("/summary", response_model=AnalyticsSummaryKPIs)
def get_analytics_summary(
    date_range: str = Query(default="30d"),
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    watershed_id: Optional[int] = Query(default=None),
    sensor_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Returns calculated analytics summary metrics: average/max rainfall, peak river level,
    average soil moisture, alert counts, sensor uptime %, and AI model error metrics (RMSE, MAE, NSE).
    """
    return AnalyticsEngine.get_summary_kpis(
        db, date_range=date_range, state=state, district=district,
        watershed_id=watershed_id, sensor_id=sensor_id
    )

@router.get("/charts", response_model=AnalyticsChartsResponse)
def get_analytics_charts(
    date_range: str = Query(default="30d"),
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    watershed_id: Optional[int] = Query(default=None),
    sensor_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Returns multi-series data for all 8 analytical charts:
    1. Rainfall history
    2. River level history
    3. Soil moisture history
    4. Flood events
    5. Risk distribution
    6. Sensor availability
    7. Alert frequency
    8. Prediction vs actual
    """
    return AnalyticsEngine.get_charts_data(
        db, date_range=date_range, state=state, district=district,
        watershed_id=watershed_id, sensor_id=sensor_id
    )

@router.get("/export/csv")
def export_analytics_csv(db: Session = Depends(get_db)):
    """
    Streams downloadable CSV report containing comprehensive catchment telemetry,
    sensor health inventory, and risk evaluations.
    """
    csv_data = AnalyticsEngine.export_csv_report(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="flash_flood_analytics_report.csv"'}
    )
