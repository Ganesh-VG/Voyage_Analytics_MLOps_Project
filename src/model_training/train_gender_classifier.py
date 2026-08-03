import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report
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


# ==================================================
# Gender Classification Model
# ==================================================

def train_gender_classifier():

    print("=" * 60)

    print("Gender Classification Model Training Started")

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
    # Select Features
    # ==========================================

    gender_df = flight_user[

        [

            "age",

            "company",

            "flightType",

            "agency",

            "distance",

            "time",

            "price",

            "gender"

        ]

    ].copy()

    # ==========================================
    # Label Encoding
    # ==========================================

    company_encoder = LabelEncoder()

    flight_encoder = LabelEncoder()

    agency_encoder = LabelEncoder()

    gender_encoder = LabelEncoder()

    gender_df["company"] = company_encoder.fit_transform(

        gender_df["company"]

    )

    gender_df["flightType"] = flight_encoder.fit_transform(

        gender_df["flightType"]

    )

    gender_df["agency"] = agency_encoder.fit_transform(

        gender_df["agency"]

    )

    gender_df["gender"] = gender_encoder.fit_transform(

        gender_df["gender"]

    )

    # ==========================================
    # Create Models Directory
    # ==========================================

    os.makedirs(

        MODELS_DIR,

        exist_ok=True

    )

    # ==========================================
    # Save Encoders
    # ==========================================

    joblib.dump(

        company_encoder,

        os.path.join(

            MODELS_DIR,

            "company_encoder.pkl"

        )

    )

    joblib.dump(

        flight_encoder,

        os.path.join(

            MODELS_DIR,

            "flight_encoder.pkl"

        )

    )

    joblib.dump(

        agency_encoder,

        os.path.join(

            MODELS_DIR,

            "agency_encoder.pkl"

        )

    )

    joblib.dump(

        gender_encoder,

        os.path.join(

            MODELS_DIR,

            "gender_encoder.pkl"

        )

    )

    print(

        "Label Encoders Saved"

    )

    # ==========================================
    # Feature Selection
    # ==========================================

    X = gender_df[

        [

            "age",

            "company",

            "flightType",

            "agency",

            "distance",

            "time",

            "price"

        ]

    ]

    y = gender_df["gender"]

    # ==========================================
    # Train Test Split
    # ==========================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y

    )

    print(

        f"Training Samples : {len(X_train)}"

    )

    print(

        f"Testing Samples : {len(X_test)}"

    )

    # ==========================================
    # Train Model
    # ==========================================

    rf_model = RandomForestClassifier(

        n_estimators=100,

        max_depth=20,

        min_samples_split=10,

        min_samples_leaf=5,

        random_state=42,

        n_jobs=-1

    )

    rf_model.fit(

        X_train,

        y_train

    )

    print(

        "Random Forest Classifier Trained"

    )

    # ==========================================
    # Predictions
    # ==========================================

    predictions = rf_model.predict(

        X_test

    )

    accuracy = accuracy_score(

        y_test,

        predictions

    )

    print("=" * 60)

    print("Model Performance")

    print("=" * 60)

    print(

        f"Accuracy : {accuracy:.4f}"

    )

    print(

        classification_report(

            y_test,

            predictions

        )

    )

    # ==========================================
    # Feature Importance
    # ==========================================

    feature_importance = pd.DataFrame(

        {

            "Feature": X.columns,

            "Importance": rf_model.feature_importances_

        }

    )

    feature_importance = feature_importance.sort_values(

        by="Importance",

        ascending=False

    )

    feature_importance.to_csv(

        os.path.join(

            MODELS_DIR,

            "gender_feature_importance.csv"

        ),

        index=False

    )

    print(

        "Feature Importance Saved"

    )

    # ==========================================
    # Save Model
    # ==========================================

    joblib.dump(

        rf_model,

        os.path.join(

            MODELS_DIR,

            "gender_classifier.pkl"

        )

    )

    model_path = os.path.join(

    MODELS_DIR,

    "gender_classifier.pkl"

    )

    joblib.dump(

        rf_model,

        model_path,

        compress=3

    )

    print(

        f"Model Size : {os.path.getsize(model_path) / (1024 * 1024):.2f} MB"

    )

    print(

        "Gender Classifier Saved Successfully"

    )

    print("=" * 60)

    print("Gender Classification Training Completed")

    print("=" * 60)


# ==================================================
# Run Script
# ==================================================

if __name__ == "__main__":

    train_gender_classifier()