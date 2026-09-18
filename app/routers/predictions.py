from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ai_forecaster import ai_forecaster
from app.models.watershed import Watershed

router = APIRouter(prefix="/predictions", tags=["AI Flood Forecasting Engine"])


class PredictionGeneratePayload(BaseModel):
    watershed_id: Optional[int] = None
    persist: bool = True


@router.post("/generate")
def generate_ai_predictions(
    payload: Optional[PredictionGeneratePayload] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Triggers AI temporal forecasting inference across catchments (or single catchment)
    and optionally persists predictions to the database.
    """
    target_id = payload.watershed_id if payload else None
    persist = payload.persist if payload else True

    if target_id:
        try:
            result = ai_forecaster.run_forecast_for_watershed(db=db, watershed_id=target_id, persist=persist)
            return {
                "status": "success",
                "count": 1,
                "results": [result]
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # Run for all watersheds
    watersheds = db.query(Watershed).all()
    results = []
    for ws in watersheds:
        try:
            res = ai_forecaster.run_forecast_for_watershed(db=db, watershed_id=ws.id, persist=persist)
            results.append(res)
        except Exception as e:
            continue

    return {
        "status": "success",
        "count": len(results),
        "results": results
    }


@router.get("/watershed/{watershed_id}")
def get_watershed_predictions(watershed_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get 30, 60, 90, 120-minute water level forecasts, flood probabilities,
    and model metadata for a given catchment.
    """
    try:
        return ai_forecaster.run_forecast_for_watershed(db=db, watershed_id=watershed_id, persist=False)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")


@router.get("/all")
def get_all_watershed_predictions(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get multi-horizon AI forecasts across all active catchments.
    """
    watersheds = db.query(Watershed).all()
    results = []
    for ws in watersheds:
        try:
            res = ai_forecaster.run_forecast_for_watershed(db=db, watershed_id=ws.id, persist=False)
            results.append(res)
        except Exception:
            continue
    return results


@router.get("/metadata")
def get_model_metadata() -> Dict[str, Any]:
    """
    Get AI forecasting model architecture, training date, feature list, and disclaimer.
    """
    return ai_forecaster.get_metadata()
