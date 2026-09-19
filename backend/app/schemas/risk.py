"""Pydantic schemas for ML Risk Prediction API."""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class RiskPredictionRequest(BaseModel):
    rainfall_mm: float = Field(..., ge=0.0, le=1000.0, json_schema_extra={"example": 180.5})
    rainfall_intensity: str = Field("moderate", json_schema_extra={"example": "heavy"})  # light, moderate, heavy, extreme
    slope_deg: float = Field(..., ge=0.0, le=90.0, json_schema_extra={"example": 32.5})
    elevation_m: float = Field(..., ge=-500.0, le=9000.0, json_schema_extra={"example": 650.0})
    soil_erodibility: float = Field(0.5, ge=0.0, le=1.0, json_schema_extra={"example": 0.75})
    land_use_type: str = Field("mixed", json_schema_extra={"example": "steep_barren"})  # dense_forest, agricultural, residential, steep_barren, mixed
    historical_disasters: int = Field(0, ge=0, json_schema_extra={"example": 2})


class RiskPredictionResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.82})
    risk_category: str = Field(..., json_schema_extra={"example": "HIGH"})  # LOW, MODERATE, HIGH, CRITICAL
    class_probabilities: Dict[str, float]
    feature_importances: Dict[str, float]
    model_version: str = Field("v1.0.0-prototype-demo", json_schema_extra={"example": "v1.0.0-prototype-demo"})
    disclaimer: str = Field(
        "PROTOTYPE DEMO MODEL: Trained on synthetic data. Not scientifically validated for operational disaster prediction.",
        json_schema_extra={"example": "PROTOTYPE DEMO MODEL: Not scientifically validated."}
    )

    model_config = ConfigDict(from_attributes=True)
