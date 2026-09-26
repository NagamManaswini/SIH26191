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
        try:
            if not os.path.exists(self.model_path):
                print(f"Model artifact not found at {self.model_path}. Auto-training prototype model...")
                self.artifact = train_and_save_model(self.model_path)
            else:
                try:
                    self.artifact = joblib.load(self.model_path)
                except Exception as e:
                    print(f"Error loading model artifact: {e}. Re-training model...")
                    self.artifact = train_and_save_model(self.model_path)

            self.model = self.artifact.get("model") if self.artifact else None
            self.scaler = self.artifact.get("scaler") if self.artifact else None
        except Exception as load_err:
            print(f"[WARNING] HazardPredictor model load/train failed: {load_err}. Using rule-based fallback predictor.")
            self.model = None
            self.scaler = None

    def predict(self, feature_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on raw feature dictionary with guaranteed fallback."""
        try:
            if self.model is None or self.scaler is None:
                self._load_model()

            if self.model is not None and self.scaler is not None:
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
                    "feature_importances": self.artifact.get("feature_importances", {}) if self.artifact else {},
                    "model_version": self.artifact.get("version", "v1.0.0-prototype-demo") if self.artifact else "v1.0.0-fallback",
                    "disclaimer": "PROTOTYPE DEMO MODEL: Not scientifically validated for operational disaster prediction.",
                }
        except ValueError:
            raise
        except Exception as pred_err:
            print(f"[WARNING] Model inference encountered error: {pred_err}. Using analytical fallback.")


        # Analytical rule-based fallback calculation (guarantees 100% uptime)
        rainfall = float(feature_input.get("rainfall_mm", 0.0) or 0.0)
        slope = float(feature_input.get("slope_deg", 15.0) or 15.0)
        intensity = str(feature_input.get("rainfall_intensity", "light") or "light").lower()

        intensity_weight = 0.25 if "extreme" in intensity else 0.15 if "heavy" in intensity else 0.05
        calc_score = min(1.0, max(0.0, (rainfall / 350.0) * 0.60 + (slope / 60.0) * 0.25 + intensity_weight))
        calc_score = round(calc_score, 4)

        cat = "CRITICAL" if calc_score > 0.75 else "HIGH" if calc_score > 0.50 else "MODERATE" if calc_score > 0.25 else "LOW"

        return {
            "risk_score": calc_score,
            "risk_category": cat,
            "class_probabilities": {
                "LOW": round(max(0.01, 1.0 - calc_score), 4),
                "MODERATE": round(0.5 * (1.0 - abs(calc_score - 0.5)), 4),
                "HIGH": round(calc_score * 0.7, 4),
                "CRITICAL": round(max(0.0, calc_score - 0.2), 4),
            },
            "feature_importances": {"rainfall_mm": 0.45, "slope_deg": 0.30, "soil_moisture": 0.15, "elevation_m": 0.10},
            "model_version": "v1.0.0-resilient-fallback",
            "disclaimer": "PROTOTYPE DEMO MODEL: Analytical fallback evaluation.",
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
