# src/models/train_gender_classifier.py

import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report
)


def train_gender_classifier():

    print("=" * 50)
    print("Training Gender Classification Model")
    print("=" * 50)

    # ==========================================
    # Load Dataset
    # ==========================================

    flight_user = pd.read_csv(
        "data/processed/flight_user.csv"
    )

    # ==========================================
    # Select Relevant Features
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
    # Encode Categorical Variables
    # ==========================================

    company_encoder = LabelEncoder()

    flight_encoder = LabelEncoder()

    agency_encoder = LabelEncoder()

    gender_encoder = LabelEncoder()

    gender_df["company"] = (
        company_encoder.fit_transform(
            gender_df["company"]
        )
    )

    gender_df["flightType"] = (
        flight_encoder.fit_transform(
            gender_df["flightType"]
        )
    )

    gender_df["agency"] = (
        agency_encoder.fit_transform(
            gender_df["agency"]
        )
    )

    gender_df["gender"] = (
        gender_encoder.fit_transform(
            gender_df["gender"]
        )
    )

    # ==========================================
    # Save Encoders
    # ==========================================

    os.makedirs(
        "models",
        exist_ok=True
    )

    joblib.dump(
        company_encoder,
        "models/company_encoder.pkl"
    )

    joblib.dump(
        flight_encoder,
        "models/flight_encoder.pkl"
    )

    joblib.dump(
        agency_encoder,
        "models/agency_encoder.pkl"
    )

    joblib.dump(
        gender_encoder,
        "models/gender_encoder.pkl"
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

    # ==========================================
    # Train Random Forest Classifier
    # ==========================================

    rf_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    rf_model.fit(
        X_train,
        y_train
    )

    # ==========================================
    # Model Evaluation
    # ==========================================

    predictions = rf_model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print(
        classification_report(
            y_test,
            predictions
        )
    )

    # ==========================================
    # Save Model
    # ==========================================

    joblib.dump(
        rf_model,
        "models/gender_classifier.pkl"
    )

    print(
        "Gender Classifier Saved Successfully"
    )


if __name__ == "__main__":

    train_gender_classifier()