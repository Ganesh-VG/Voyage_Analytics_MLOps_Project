from flask import Flask, request, jsonify

import pandas as pd
import joblib
import os

app = Flask(__name__)

# ==================================================
# Load Models
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODELS_DIR = os.path.join(
    BASE_DIR,
    "models"
)

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

hotel_recommendation = joblib.load(
    os.path.join(
        MODELS_DIR,
        "hotel_recommendation.pkl"
    )
)

# ==================================================
# Load Preprocessing Artifacts
# ==================================================

flight_columns = joblib.load(
    os.path.join(
        MODELS_DIR,
        "flight_columns.pkl"
    )
)

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

# ==================================================
# Home Route
# ==================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Voyage Analytics API Running Successfully"
    })

# ==================================================
# Flight Price Prediction
# ==================================================

@app.route(
    "/predict_price",
    methods=["POST"]
)
def predict_price():

    try:

        data = request.json

        features = pd.DataFrame(
            [data]
        )

        features = pd.get_dummies(
            features
        )

        features = features.reindex(
            columns=flight_columns,
            fill_value=0
        )

        prediction = flight_model.predict(
            features
        )[0]

        return jsonify({
            "predicted_price":
            round(
                float(prediction),
                2
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })

# ==================================================
# Gender Classification
# ==================================================

@app.route(
    "/predict_gender",
    methods=["POST"]
)
def predict_gender():

    try:

        data = request.json

        features = pd.DataFrame(
            [data]
        )

        features["company"] = (
            company_encoder.transform(
                features["company"]
            )
        )

        features["flightType"] = (
            flight_encoder.transform(
                features["flightType"]
            )
        )

        features["agency"] = (
            agency_encoder.transform(
                features["agency"]
            )
        )

        prediction = gender_model.predict(
            features
        )[0]

        gender_value = (
            gender_encoder.inverse_transform(
                [prediction]
            )[0]
        )

        return jsonify({
            "predicted_gender":
            gender_value
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })

# ==================================================
# Hotel Recommendation
# ==================================================

@app.route(
    "/recommend_hotel",
    methods=["POST"]
)
def recommend_hotel():

    try:

        destination = request.json[
            "destination"
        ]

        recommendations = (
            hotel_recommendation[
                hotel_recommendation["place"]
                == destination
            ]
        )

        return recommendations.to_json(
            orient="records"
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        })

# ==================================================
# Run App
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )