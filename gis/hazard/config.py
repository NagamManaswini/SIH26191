"""Configurable threshold parameters and weights for baseline hazard score computation."""

from pydantic import BaseModel, Field


class HazardConfig(BaseModel):
    # Weights summing to 1.0
    weight_rainfall: float = Field(0.35, ge=0.0, le=1.0)
    weight_slope: float = Field(0.30, ge=0.0, le=1.0)
    weight_elevation: float = Field(0.15, ge=0.0, le=1.0)
    weight_soil: float = Field(0.10, ge=0.0, le=1.0)
    weight_historical: float = Field(0.10, ge=0.0, le=1.0)

    # Category Thresholds
    threshold_low: float = Field(0.25, ge=0.0, le=1.0)
    threshold_moderate: float = Field(0.50, ge=0.0, le=1.0)
    threshold_high: float = Field(0.75, ge=0.0, le=1.0)

    def classify_score(self, score: float) -> str:
        """Classify numerical hazard score (0.0 to 1.0) into LOW, MODERATE, HIGH, or CRITICAL."""
        if score < self.threshold_low:
            return "LOW"
        elif score < self.threshold_moderate:
            return "MODERATE"
        elif score < self.threshold_high:
            return "HIGH"
        else:
            return "CRITICAL"


default_hazard_config = HazardConfig()
