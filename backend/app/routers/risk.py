from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.risk import RiskPredictionRequest, RiskPredictionResponse
from ml.inference import get_predictor

router = APIRouter(prefix="/risk", tags=["Machine Learning Risk Prediction"])


@router.post("/predict", response_model=RiskPredictionResponse, status_code=status.HTTP_200_OK)
def predict_hazard_risk(req: RiskPredictionRequest):
    """Predict disaster hazard risk score and category using prototype XGBoost Machine Learning model.

    Safety Disclaimer:
    PROTOTYPE DEMO MODEL: Trained on synthetic data. Not scientifically validated for operational disaster prediction.
    """
    try:
        predictor = get_predictor()
        input_dict = req.model_dump()
        result = predictor.predict(input_dict)
        return RiskPredictionResponse.model_validate(result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk prediction model evaluation failed: {str(e)}",
        )
