from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.risk_engine import risk_engine
from app.models.watershed import Watershed
from app.models.risk_config import RiskConfiguration

router = APIRouter(prefix="/risk", tags=["Explainable Flood Risk Engine"])


class RiskConfigUpdatePayload(BaseModel):
    config_name: Optional[str] = None
    weight_rainfall: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_accumulated_rain: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_river_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_rate_of_rise: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_soil_moisture: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_slope: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight_historical: Optional[float] = Field(None, ge=0.0, le=1.0)
    threshold_rainfall_moderate_mm: Optional[float] = None
    threshold_rainfall_critical_mm: Optional[float] = None
    threshold_accumulated_rain_3h_mm: Optional[float] = None
    threshold_river_danger_m: Optional[float] = None
    threshold_river_critical_m: Optional[float] = None
    threshold_rate_of_rise_m_hr: Optional[float] = None
    threshold_soil_critical_pct: Optional[float] = None
    threshold_slope_steep_deg: Optional[float] = None


@router.get("/watershed/{watershed_id}")
def get_watershed_risk_evaluation(watershed_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get explainable multi-factor flood risk evaluation, factor breakdown,
    plain-language explanations, and historical comparison for a given watershed.
    """
    try:
        return risk_engine.evaluate_watershed_risk(watershed_id=watershed_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate risk: {str(e)}")


@router.get("/all")
def get_all_watersheds_risk_matrix(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get live explainable risk assessments for all catchments.
    """
    watersheds = db.query(Watershed).all()
    results = []
    for ws in watersheds:
        try:
            eval_res = risk_engine.evaluate_watershed_risk(watershed_id=ws.id, db=db)
            results.append(eval_res)
        except Exception as e:
            continue
    return results


@router.get("/configuration")
def get_risk_configuration(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get the currently active flood risk scoring weights and threshold configuration.
    """
    config = risk_engine.get_active_configuration(db)
    return {
        "id": config.id,
        "config_name": config.config_name,
        "is_active": config.is_active,
        "weights": {
            "rainfall": config.weight_rainfall,
            "accumulated_rain": config.weight_accumulated_rain,
            "river_level": config.weight_river_level,
            "rate_of_rise": config.weight_rate_of_rise,
            "soil_moisture": config.weight_soil_moisture,
            "slope": config.weight_slope,
            "historical": config.weight_historical
        },
        "thresholds": {
            "rainfall_moderate_mm": config.threshold_rainfall_moderate_mm,
            "rainfall_critical_mm": config.threshold_rainfall_critical_mm,
            "accumulated_rain_3h_mm": config.threshold_accumulated_rain_3h_mm,
            "river_danger_m": config.threshold_river_danger_m,
            "river_critical_m": config.threshold_river_critical_m,
            "rate_of_rise_m_hr": config.threshold_rate_of_rise_m_hr,
            "soil_critical_pct": config.threshold_soil_critical_pct,
            "slope_steep_deg": config.threshold_slope_steep_deg
        },
        "updated_at": config.updated_at.isoformat() if config.updated_at else None
    }


@router.put("/configuration")
def update_risk_configuration(payload: RiskConfigUpdatePayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Update flood risk scoring weights and thresholds dynamically.
    """
    config = risk_engine.get_active_configuration(db)

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None and hasattr(config, key):
            setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return get_risk_configuration(db)
