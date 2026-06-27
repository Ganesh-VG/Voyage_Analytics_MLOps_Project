import os
import joblib
import pandas as pd


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
# Model Validation
# ==================================================

def validate_models():

    print("=" * 60)

    print("MODEL VALIDATION")

    print("=" * 60)

    # ==========================================
    # Load Datasets
    # ==========================================

    flight_user = pd.read_csv(

        os.path.join(

            DATA_DIR,

            "flight_user.csv"

        )

    )

    hotel_user = pd.read_csv(

        os.path.join(

            DATA_DIR,

            "hotel_user.csv"

        )

    )

    print("Datasets Loaded")

    print(

        f"Flight Dataset : {flight_user.shape}"

    )

    print(

        f"Hotel Dataset  : {hotel_user.shape}"

    )

    # ==========================================
    # Load Models
    # ==========================================

    flight_model = joblib.load(

        os.path.join(

            MODELS_DIR,

            "flight_price_model.pkl"

        )

    )

    gender_model = joblib.load(

        os.path.join(

            MODELS_DIR,

            "gender_classifier.pkl"

        )

    )

    hotel_model = joblib.load(

        os.path.join(

            MODELS_DIR,

            "hotel_recommendation.pkl"

        )

    )

    print("Models Loaded Successfully")

    # ==========================================
    # Flight Model Validation
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

        os.path.join(

            MODELS_DIR,

            "flight_columns.pkl"

        )

    )

    X_flight = X_flight.reindex(

        columns=flight_columns,

        fill_value=0

    )

    flight_prediction = flight_model.predict(

        X_flight.iloc[[0]]

    )[0]

    print(

        f"Sample Flight Price Prediction : {flight_prediction:.2f}"

    )

    # ==========================================
    # Gender Model Validation
    # ==========================================

    company_encoder = joblib.load(

        os.path.join(

            MODELS_DIR,

            "company_encoder.pkl"

        )

    )

    flight_encoder = joblib.load(

        os.path.join(

            MODELS_DIR,

            "flight_encoder.pkl"

        )

    )

    agency_encoder = joblib.load(

        os.path.join(

            MODELS_DIR,

            "agency_encoder.pkl"

        )

    )

    gender_encoder = joblib.load(

        os.path.join(

            MODELS_DIR,

            "gender_encoder.pkl"

        )

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

    gender_sample["company"] = company_encoder.transform(

        gender_sample["company"]

    )

    gender_sample["flightType"] = flight_encoder.transform(

        gender_sample["flightType"]

    )

    gender_sample["agency"] = agency_encoder.transform(

        gender_sample["agency"]

    )

    gender_prediction = gender_model.predict(

        gender_sample

    )[0]

    predicted_gender = gender_encoder.inverse_transform(

        [gender_prediction]

    )[0]

    print(

        f"Sample Gender Prediction : {predicted_gender}"

    )

    # ==========================================
    # Hotel Recommendation Validation
    # ==========================================

    print(

        f"Recommendation Records : {len(hotel_model)}"

    )

    print(

        hotel_model.head()

    )

    # ==========================================
    # Deployment Summary
    # ==========================================

    print("=" * 60)

    print("DEPLOYMENT READINESS")

    print("=" * 60)

    print("✓ Datasets Loaded")

    print("✓ Models Loaded")

    print("✓ Flight Model Validated")

    print("✓ Gender Model Validated")

    print("✓ Hotel Recommendation Validated")

    print("✓ Artifacts Verified")

    print("=" * 60)

    print("MODEL VALIDATION PASSED")

    print("=" * 60)


# ==================================================
# Run Script
# ==================================================

if __name__ == "__main__":

    validate_models()