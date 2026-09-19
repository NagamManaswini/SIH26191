"""Inference engine for loading serialized XGBoost hazard risk prediction model."""

import os
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

from ml.features.feature_extractor import extract_features_from_dict, FEATURE_NAMES
from ml.training.train import MODEL_PATH, train_and_save_model

CATEGORY_NAMES = {
    0: "LOW",
    1: "MODERATE",
    2: "HIGH",
    3: "CRITICAL",
}


class HazardPredictor:
    """Inference engine for XGBoost hazard risk prediction."""

    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.artifact: Optional[Dict[str, Any]] = None
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        """Load joblib artifact or auto-train if missing."""
        if not os.path.exists(self.model_path):
            print(f"Model artifact not found at {self.model_path}. Auto-training prototype model...")
            self.artifact = train_and_save_model(self.model_path)
        else:
            try:
                self.artifact = joblib.load(self.model_path)
            except Exception as e:
                print(f"Error loading model artifact: {e}. Re-training model...")
                self.artifact = train_and_save_model(self.model_path)

        self.model = self.artifact.get("model")
        self.scaler = self.artifact.get("scaler")

    def predict(self, feature_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on raw feature dictionary."""
        if self.model is None or self.scaler is None:
            self._load_model()

        # 1. Extract feature array and wrap in DataFrame with feature names
        X_raw = extract_features_from_dict(feature_input)
        df_raw = pd.DataFrame(X_raw, columns=FEATURE_NAMES)

        # 2. Scale features
        X_scaled = self.scaler.transform(df_raw)

        # 3. Predict class and probabilities
        pred_class = int(self.model.predict(X_scaled)[0])
        probabilities = self.model.predict_proba(X_scaled)[0]

        # Continuous risk score estimate (weighted probability sum)
        risk_score = float(np.sum(probabilities * np.array([0.15, 0.40, 0.65, 0.90])))
        risk_score = float(round(np.clip(risk_score, 0.0, 1.0), 4))

        category = CATEGORY_NAMES.get(pred_class, "MODERATE")

        return {
            "risk_score": risk_score,
            "risk_category": category,
            "class_probabilities": {
                "LOW": round(float(probabilities[0]), 4),
                "MODERATE": round(float(probabilities[1]), 4),
                "HIGH": round(float(probabilities[2]), 4),
                "CRITICAL": round(float(probabilities[3]), 4),
            },
            "feature_importances": self.artifact.get("feature_importances", {}),
            "model_version": self.artifact.get("version", "v1.0.0-prototype-demo"),
            "disclaimer": self.artifact.get(
                "disclaimer",
                "PROTOTYPE DEMO MODEL: Not scientifically validated for operational disaster prediction."
            ),
        }


# Global predictor instance singleton
_default_predictor: Optional[HazardPredictor] = None


def get_predictor() -> HazardPredictor:
    """Get or create singleton HazardPredictor instance."""
    global _default_predictor
    if _default_predictor is None:
        _default_predictor = HazardPredictor()
    return _default_predictor


def predict_hazard_risk(feature_input: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to run inference using singleton predictor."""
    return get_predictor().predict(feature_input)
