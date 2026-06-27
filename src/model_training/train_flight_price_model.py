import pandas as pd
import numpy as np

import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import mlflow
import mlflow.sklearn

# ==========================================
# MLflow Configuration
# ==========================================

mlflow.set_tracking_uri(
    "sqlite:///mlflow.db"
)

mlflow.set_experiment(
    "Flight Price Prediction"
)


def train_flight_price_model():

    print("=" * 50)
    print("Training Flight Price Model")
    print("=" * 50)

    # ==========================================
    # Load Dataset
    # ==========================================

    flight_user = pd.read_csv(
        "data/processed/flight_user.csv"
    )

    # ==========================================
    # Features
    # ==========================================

    feature_columns = [
        "distance",
        "time",
        "flightType",
        "agency",
        "from",
        "to",
        "month"
    ]

    X = flight_user[
        feature_columns
    ]

    y = flight_user[
        "price"
    ]

    # ==========================================
    # Encoding
    # ==========================================

    X = pd.get_dummies(
        X,
        columns=[
            "flightType",
            "agency",
            "from",
            "to"
        ],
        drop_first=True
    )

    # ==========================================
    # Save Deployment Columns
    # ==========================================

    os.makedirs(
        "models",
        exist_ok=True
    )

    joblib.dump(
        X.columns.tolist(),
        "models/flight_columns.pkl"
    )

    # ==========================================
    # Train Test Split
    # ==========================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

# ==========================================
# Train Model & Track with MLflow
# ==========================================

with mlflow.start_run(
    run_name="Random Forest"
):

    rf = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    rf.fit(
        X_train,
        y_train
    )

    predictions = rf.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2  : {r2:.4f}")

    # ==========================================
    # Save Model
    # ==========================================

    joblib.dump(
        rf,
        "models/flight_price_model.pkl"
    )

    # ==========================================
    # Save Feature Columns
    # ==========================================

    joblib.dump(
        X.columns.tolist(),
        "models/flight_columns.pkl"
    )

    # ==========================================
    # Feature Importance
    # ==========================================

    feature_importance = pd.DataFrame({

        "Feature": X.columns,

        "Importance": rf.feature_importances_

    })

    feature_importance = feature_importance.sort_values(

        by="Importance",

        ascending=False

    )

    feature_importance.to_csv(

        "models/feature_importance.csv",

        index=False

    )

    # ==========================================
    # MLflow Parameters
    # ==========================================

    mlflow.log_param(
        "model_type",
        "RandomForestRegressor"
    )

    mlflow.log_param(
        "n_estimators",
        100
    )

    mlflow.log_param(
        "random_state",
        42
    )

    mlflow.log_param(
        "dataset_rows",
        len(flight_user)
    )

    mlflow.log_param(
        "feature_count",
        X.shape[1]
    )

    # ==========================================
    # MLflow Metrics
    # ==========================================

    mlflow.log_metric(
        "MAE",
        mae
    )

    mlflow.log_metric(
        "RMSE",
        rmse
    )

    mlflow.log_metric(
        "R2",
        r2
    )

    # ==========================================
    # MLflow Model
    # ==========================================

    mlflow.sklearn.log_model(

        rf,

        artifact_path="flight_price_model"

    )

    # ==========================================
    # MLflow Artifacts
    # ==========================================

    mlflow.log_artifact(
        "models/flight_price_model.pkl"
    )

    mlflow.log_artifact(
        "models/flight_columns.pkl"
    )

    mlflow.log_artifact(
        "models/feature_importance.csv"
    )

    print("=" * 50)
    print("Training Completed Successfully")
    print("=" * 50)

    # ==========================================
    # Evaluation
    # ==========================================

    predictions = rf.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print(
        f"MAE : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R2 : {r2:.4f}"
    )

    # ==========================================
    # Save Model
    # ==========================================

    joblib.dump(
        rf,
        "models/flight_price_model.pkl"
    )

    print(
        "Flight Price Model Saved"
    )


if __name__ == "__main__":

    train_flight_price_model()