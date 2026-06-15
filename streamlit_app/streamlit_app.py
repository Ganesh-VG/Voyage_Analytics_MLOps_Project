import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Voyage Analytics",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Voyage Analytics MLOps Project")

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Flight Price Prediction",
        "Gender Classification",
        "Hotel Recommendation"
    ]
)

# ==================================================
# Flight Price Prediction
# ==================================================

if menu == "Flight Price Prediction":

    st.header("Flight Price Prediction")

    distance = st.number_input(
        "Distance",
        min_value=0.0
    )

    time = st.number_input(
        "Travel Time",
        min_value=0.0
    )

    # month = st.number_input(
    #     "Month",
    #     min_value=1,
    #     max_value=12
    # )

    # flight_type = st.selectbox(
    #     "Flight Type",
    #     [
    #         "economic",
    #         "premium",
    #         "firstClass"
    #     ]
    # )

    # agency = st.selectbox(
    #     "Agency",
    #     [
    #         "CloudFy",
    #         "FlyingDrops",
    #         "Rainbow"
    #     ]
    # )

    # origin = st.text_input(
    #     "From"
    # )

    # destination = st.text_input(
    #     "To"
    # )

    flight_df = pd.read_csv(
    "../data/processed/flight_user.csv"
    )

    origin = st.selectbox(
        "From",
        sorted(
            flight_df["from"].unique()
        )
    )

    destination = st.selectbox(
        "To",
        sorted(
            flight_df["to"].unique()
        )
    )

    agency = st.selectbox(
    "Agency",
    sorted(
        flight_df["agency"].unique()
    )
    )

    flight_type = st.selectbox(
        "Flight Type",
        sorted(
            flight_df["flightType"].unique()
        )
    )

    month = st.selectbox(
        "Month",
        list(range(1, 13))
    )

    if st.button(
        "Predict Price"
    ):

        payload = {
            "distance": distance,
            "time": time,
            "month": month,
            "flightType": flight_type,
            "agency": agency,
            "from": origin,
            "to": destination
        }

        response = requests.post(
            "http://localhost:5000/predict_price",
            json=payload
        )

        st.success(
            response.json()
        )

# ==================================================
# Gender Classification
# ==================================================

elif menu == "Gender Classification":

    st.header(
        "Gender Classification"
    )

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100
    )

    company = st.number_input(
        "Company Code",
        min_value=0
    )

    trip_count = st.number_input(
        "Trip Count",
        min_value=0
    )

    avg_flight_price = st.number_input(
        "Average Flight Price"
    )

    avg_distance = st.number_input(
        "Average Distance"
    )

    avg_travel_time = st.number_input(
        "Average Travel Time"
    )

    avg_hotel_spend = st.number_input(
        "Average Hotel Spend"
    )

    avg_stay_days = st.number_input(
        "Average Stay Days"
    )

    flight_type = st.number_input(
        "Flight Type Encoded"
    )

    agency = st.number_input(
        "Agency Encoded"
    )

    if st.button(
        "Predict Gender"
    ):

        payload = {
            "age": age,
            "company": company,
            "trip_count": trip_count,
            "avg_flight_price": avg_flight_price,
            "avg_distance": avg_distance,
            "avg_travel_time": avg_travel_time,
            "avg_hotel_spend": avg_hotel_spend,
            "avg_stay_days": avg_stay_days,
            "flightType": flight_type,
            "agency": agency
        }

        response = requests.post(
            "http://localhost:5000/predict_gender",
            json=payload
        )

        st.success(
            response.json()
        )

# ==================================================
# Hotel Recommendation
# ==================================================

else:

    st.header(
        "Hotel Recommendation"
    )

    destination = st.selectbox(
        "Destination",
        [
            "Salvador (BH)",
            "Rio de Janeiro (RJ)",
            "Natal (RN)",
            "Sao Paulo (SP)",
            "Recife (PE)",
            "Brasilia (DF)",
            "Campo Grande (MS)",
            "Aracaju (SE)",
            "Florianopolis (SC)"
        ]
    )

    if st.button(
        "Recommend Hotel"
    ):

        payload = {
            "destination": destination
        }

        response = requests.post(
            "http://localhost:5000/recommend_hotel",
            json=payload
        )

        result = pd.DataFrame(
            response.json()
        )

        st.dataframe(
            result
        )