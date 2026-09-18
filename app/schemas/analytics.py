from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PredictionMetrics(BaseModel):
    rmse_m: float
    mae_m: float
    nse_coefficient: float
    r2_score: float
    sample_count: int

class AnalyticsSummaryKPIs(BaseModel):
    average_rainfall_mm: float
    maximum_rainfall_mm: float
    maximum_river_level_m: float
    average_soil_moisture_pct: float
    total_alerts_count: int
    critical_events_count: int
    sensor_uptime_pct: float
    prediction_metrics: PredictionMetrics
    active_monitoring_period: str
    last_updated: str

class ChartDataPoint(BaseModel):
    timestamp: str
    value: float
    secondary_value: Optional[float] = None
    label: Optional[str] = None
    category: Optional[str] = None

class HistoricalFloodItem(BaseModel):
    id: int
    name: str
    location: str
    start_time: str
    end_time: Optional[str] = None
    maximum_rainfall: float
    maximum_water_level: float
    affected_area: str
    severity: str

class RiskDistributionItem(BaseModel):
    risk_level: str
    percentage: float
    count: int
    color: str

class SensorAvailabilityItem(BaseModel):
    sensor_type: str
    online_count: int
    total_count: int
    uptime_percentage: float

class AlertFrequencyItem(BaseModel):
    date: str
    info_count: int
    warning_count: int
    danger_count: int
    emergency_count: int
    total: int

class PredictionVsActualPoint(BaseModel):
    timestamp: str
    actual_water_level_m: float
    predicted_water_level_m: float
    residual_error_m: float
    lead_time_min: int

class AnalyticsChartsResponse(BaseModel):
    time_window: str
    rainfall_history: List[ChartDataPoint]
    river_level_history: List[ChartDataPoint]
    soil_moisture_history: List[ChartDataPoint]
    historical_flood_events: List[HistoricalFloodItem]
    risk_distribution: List[RiskDistributionItem]
    sensor_availability: List[SensorAvailabilityItem]
    alert_frequency: List[AlertFrequencyItem]
    prediction_vs_actual: List[PredictionVsActualPoint]
