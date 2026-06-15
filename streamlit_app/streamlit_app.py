import streamlit as st
import pandas as pd
import requests

flight_df = pd.read_csv(
    "../data/processed/flight_user.csv"
)

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

    age = st.slider(
        "Age",
        min_value=int(
            flight_df["age"].min()
        ),
        max_value=int(
            flight_df["age"].max()
        ),
        value=30
    )

    company = st.selectbox(
        "Company",
        sorted(
            flight_df["company"].unique()
        )
    )

    flight_type = st.selectbox(
        "Flight Type",
        sorted(
            flight_df["flightType"].unique()
        )
    )

    agency = st.selectbox(
        "Agency",
        sorted(
            flight_df["agency"].unique()
        )
    )

    distance = st.selectbox(
        "Distance",
        sorted(
            flight_df["distance"].unique()
        )
    )

    time = st.selectbox(
        "Travel Time",
        sorted(
            flight_df["time"].unique()
        )
    )

    price = st.selectbox(
        "Flight Price",
        sorted(
            flight_df["price"].unique()
        )
    )

    if st.button(
        "Predict Gender"
    ):

        payload = {
            "age": age,
            "company": company,
            "flightType": flight_type,
            "agency": agency,
            "distance": distance,
            "time": time,
            "price": price
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