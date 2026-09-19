"""XGBoost model training, preprocessing pipeline, and model serialization."""

import os
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from ml.data.dataset_loader import generate_synthetic_training_dataframe
from ml.features.feature_extractor import FEATURE_NAMES
from ml.evaluation.metrics import evaluate_model_performance

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_hazard_model.joblib")


def train_and_save_model(save_path: str = MODEL_PATH) -> Dict[str, Any]:
    """Train XGBoost model on synthetic dataset, evaluate metrics, and save serialized joblib artifact."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 1. Load training dataset
    df = generate_synthetic_training_dataframe(num_samples=1500, seed=42)
    X = df[FEATURE_NAMES]
    y = df["risk_category"]

    # 2. Train/test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 3. Fit StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train XGBoost Classifier
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
    )
    model.fit(X_train_scaled, y_train)

    # 5. Evaluate test set predictions
    y_pred = model.predict(X_test_scaled)
    metrics = evaluate_model_performance(y_test, y_pred)

    # Feature importances dictionary
    importances = dict(zip(FEATURE_NAMES, [float(round(v, 4)) for v in model.feature_importances_]))

    # 6. Save serialized model payload
    artifact_payload = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "version": "v1.0.0-prototype-demo",
        "metrics": metrics,
        "feature_importances": importances,
        "disclaimer": "PROTOTYPE DEMO MODEL: Trained on synthetic data. Not scientifically validated for operational disaster management.",
    }
    joblib.dump(artifact_payload, save_path)
    print(f"Successfully trained and saved model artifact to: {save_path}")

    return artifact_payload


if __name__ == "__main__":
    train_and_save_model()
