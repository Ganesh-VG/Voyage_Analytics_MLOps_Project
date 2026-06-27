import os
import joblib
import mlflow
import mlflow.sklearn

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==================================================
# Project Paths
# ==================================================

BASE_DIR = os.environ.get(

    "PROJECT_ROOT",

    os.path.abspath(

        os.path.join(

            os.path.dirname(__file__),

            "..",

            ".."

        )

    )

)

DATA_DIR = os.path.join(

    BASE_DIR,

    "data",

    "processed"

)

MODELS_DIR = os.path.join(

    BASE_DIR,

    "models"

)

MLFLOW_DIR = os.path.join(

    BASE_DIR,

    "mlflow"

)

os.makedirs(

    MLFLOW_DIR,

    exist_ok=True

)

MLFLOW_DB = os.path.join(

    MLFLOW_DIR,

    "mlflow.db"

)


# ==================================================
# MLflow Configuration
# ==================================================

mlflow.set_tracking_uri(

    f"sqlite:///{MLFLOW_DB}"

)

mlflow.set_experiment(

    "Flight Price Prediction"

)


# ==================================================
# Flight Price Model Training
# ==================================================

def train_flight_price_model():

    print("=" * 60)

    print("Flight Price Model Training Started")

    print("=" * 60)

    # ==========================================
    # Load Dataset
    # ==========================================

    flight_user = pd.read_csv(

        os.path.join(

            DATA_DIR,

            "flight_user.csv"

        )

    )

    print(

        f"Dataset Shape : {flight_user.shape}"

    )

    # ==========================================
    # Feature Selection
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

    target_column = "price"

    X = flight_user[

        feature_columns

    ]

    y = flight_user[

        target_column

    ]

    print(

        f"Feature Matrix Shape : {X.shape}"

    )

    print(

        f"Target Shape : {y.shape}"

    )

    # ==========================================
    # Encode Categorical Features
    # ==========================================

    categorical_columns = [

        "flightType",

        "agency",

        "from",

        "to"

    ]

    X = pd.get_dummies(

        X,

        columns=categorical_columns,

        drop_first=True

    )

    print(

        f"Encoded Feature Shape : {X.shape}"

    )

    # ==========================================
    # Create Models Folder
    # ==========================================

    os.makedirs(

        MODELS_DIR,

        exist_ok=True

    )

    # ==========================================
    # Save Deployment Feature Columns
    # ==========================================

    joblib.dump(

        X.columns.tolist(),

        os.path.join(

            MODELS_DIR,

            "flight_columns.pkl"

        )

    )

    print(

        "Deployment Feature Columns Saved"

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

    print(

        f"Training Samples : {len(X_train)}"

    )

    print(

        f"Testing Samples : {len(X_test)}"

    )

    # ==========================================
    # Train Model & Track with MLflow
    # ==========================================

    with mlflow.start_run(
        run_name="Random Forest"
    ):

        # ==========================================
        # Model Training
        # ==========================================

        rf = RandomForestRegressor(

            n_estimators=100,

            random_state=42

        )

        rf.fit(

            X_train,

            y_train

        )

        print(
            "Random Forest Model Trained Successfully"
        )

        # ==========================================
        # Predictions
        # ==========================================

        predictions = rf.predict(

            X_test

        )

        # ==========================================
        # Model Evaluation
        # ==========================================

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

        print("=" * 60)

        print("Model Performance")

        print("=" * 60)

        print(f"MAE  : {mae:.4f}")

        print(f"RMSE : {rmse:.4f}")

        print(f"R2   : {r2:.4f}")

        # ==========================================
        # Save Trained Model
        # ==========================================

        joblib.dump(

            rf,

            os.path.join(

                MODELS_DIR,

                "flight_price_model.pkl"

            )

        )

        print(
            "Flight Price Model Saved"
        )

        # ==========================================
        # Feature Importance
        # ==========================================

        feature_importance = pd.DataFrame(

            {

                "Feature": X.columns,

                "Importance": rf.feature_importances_

            }

        )

        feature_importance = feature_importance.sort_values(

            by="Importance",

            ascending=False

        )

        feature_importance.to_csv(

            os.path.join(

                MODELS_DIR,

                "feature_importance.csv"

            ),

            index=False

        )

        print(
            "Feature Importance Saved"
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
        # Log ML Model
        # ==========================================

        mlflow.sklearn.log_model(

            sk_model=rf,

            artifact_path="flight_price_model"

        )

        # ==========================================
        # Log Artifacts
        # ==========================================

        mlflow.log_artifact(

            os.path.join(

                MODELS_DIR,

                "flight_price_model.pkl"

            )

        )

        mlflow.log_artifact(

            os.path.join(

                MODELS_DIR,

                "flight_columns.pkl"

            )

        )

        mlflow.log_artifact(

            os.path.join(

                MODELS_DIR,

                "feature_importance.csv"

            )

        )

        print("=" * 60)

        print("MLflow Logging Completed")

        print("=" * 60)

    print("=" * 60)

    print("Flight Price Model Training Completed Successfully")

    print("=" * 60)


# ==================================================
# Run Script
# ==================================================

if __name__ == "__main__":

    train_flight_price_model()