import pandas as pd
import joblib


def validate_models():

    print("=" * 50)
    print("MODEL VALIDATION")
    print("=" * 50)

    # ==========================================
    # Load Datasets
    # ==========================================

    flight_user = pd.read_csv(
        "data/processed/flight_user.csv"
    )

    hotel_user = pd.read_csv(
        "data/processed/hotel_user.csv"
    )

    print("Datasets Loaded")

    # ==========================================
    # Load Models
    # ==========================================

    flight_model = joblib.load(
        "models/flight_price_model.pkl"
    )

    gender_model = joblib.load(
        "models/gender_classifier.pkl"
    )

    hotel_model = joblib.load(
        "models/hotel_recommendation.pkl"
    )

    print("Models Loaded")

    # ==========================================
    # Flight Validation
    # ==========================================

    X_flight = flight_user[
        [
            "distance",
            "time",
            "flightType",
            "agency",
            "from",
            "to",
            "month"
        ]
    ]

    X_flight = pd.get_dummies(
        X_flight,
        columns=[
            "flightType",
            "agency",
            "from",
            "to"
        ],
        drop_first=True
    )

    flight_columns = joblib.load(
        "models/flight_columns.pkl"
    )

    X_flight = X_flight.reindex(
        columns=flight_columns,
        fill_value=0
    )

    flight_prediction = (
        flight_model.predict(
            X_flight.iloc[[0]]
        )[0]
    )

    print(
        "Flight Prediction:",
        flight_prediction
    )

    # ==========================================
    # Gender Validation
    # ==========================================

    company_encoder = joblib.load(
        "models/company_encoder.pkl"
    )

    flight_encoder = joblib.load(
        "models/flight_encoder.pkl"
    )

    agency_encoder = joblib.load(
        "models/agency_encoder.pkl"
    )

    gender_sample = flight_user[
        [
            "age",
            "company",
            "flightType",
            "agency",
            "distance",
            "time",
            "price"
        ]
    ].iloc[[0]].copy()

    gender_sample["company"] = (
        company_encoder.transform(
            gender_sample["company"]
        )
    )

    gender_sample["flightType"] = (
        flight_encoder.transform(
            gender_sample["flightType"]
        )
    )

    gender_sample["agency"] = (
        agency_encoder.transform(
            gender_sample["agency"]
        )
    )

    gender_prediction = (
        gender_model.predict(
            gender_sample
        )[0]
    )

    print(
        "Gender Prediction:",
        gender_prediction
    )

    # ==========================================
    # Hotel Validation
    # ==========================================

    print(
        hotel_model.head()
    )

    print("=" * 50)
    print("VALIDATION PASSED")
    print("=" * 50)


if __name__ == "__main__":

    validate_models()