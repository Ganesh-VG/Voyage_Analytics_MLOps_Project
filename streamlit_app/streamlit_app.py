import streamlit as st
import pandas as pd
import requests
import os


# Configure this value for Kubernetes without changing application code.
# Example outside Minikube: http://<minikube-ip>:30080
# Example inside the cluster: http://voyage-api-service.voyage-analytics.svc.cluster.local:8000
API_BASE_URL = os.getenv(
    "VOYAGE_API_BASE_URL",
    "http://localhost:8000"
).rstrip("/")

flight_df = pd.read_csv(
    "./data/processed/flight_user.csv"
)

st.set_page_config(
    page_title="Voyage Analytics",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Voyage Analytics MLOps Project")

st.caption(
    f"API endpoint: {API_BASE_URL}"
)

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

# if menu == "Flight Price Prediction":

#     st.header(
#         "Flight Price Prediction"
#     )

#     flight_df = pd.read_csv(
#         "./data/processed/flight_user.csv"
# )

#     origin = st.selectbox(
#         "From",
#         sorted(
#             flight_df["from"].unique()
#         )
#     )

#     destination = st.selectbox(
#         "To",
#         sorted(
#             flight_df["to"].unique()
#         )
#     )

#     agency = st.selectbox(
#         "Agency",
#         sorted(
#             flight_df["agency"].unique()
#         )
#     )

#     flight_type = st.selectbox(
#         "Flight Type",
#         sorted(
#             flight_df["flightType"].unique()
#         )
#     )

#     month = st.selectbox(
#         "Month",
#         list(range(1, 13))
#     )

#     route_data = flight_df[
#         (flight_df["from"] == origin)
#         &
#         (flight_df["to"] == destination)
#     ]

#     if len(route_data) > 0:

#         distance = float(
#             route_data["distance"].iloc[0]
#         )

#         travel_time = float(
#             route_data["time"].iloc[0]
#         )

#         st.info(
#             f"Distance: {distance} km"
#         )

#         st.info(
#             f"Travel Time: {travel_time} hrs"
#         )

#     if st.button(
#         "Predict Price"
#     ):

#         payload = {
#             "distance": distance,
#             "time": travel_time,
#             "month": month,
#             "flightType": flight_type,
#             "agency": agency,
#             "from": origin,
#             "to": destination
#         }

#         response = requests.post(
#             "http://localhost:8000/predict_price",
#             json=payload
#         )

#         st.success(
#             response.json()
#         )


# ==================================================
# Flight Price Prediction
# ==================================================

if menu == "Flight Price Prediction":

    st.header(
        "Flight Price Prediction"
    )

    flight_df = pd.read_csv(
        "./data/processed/flight_user.csv"
    )

    origin = st.selectbox(
        "From",
        sorted(
            flight_df["from"].unique()
        )
    )

    valid_destinations = sorted(
        flight_df[
            flight_df["from"] == origin
        ]["to"].unique()
    )

    destination = st.selectbox(
        "To",
        valid_destinations
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

    route_data = flight_df[
        (flight_df["from"] == origin)
        &
        (flight_df["to"] == destination)
    ]

    distance = None
    travel_time = None

    if not route_data.empty:

        distance = round(
            float(
                route_data["distance"].mean()
            ),
            2
        )

        travel_time = round(
            float(
                route_data["time"].mean()
            ),
            2
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Distance (km)",
                distance
            )

        with col2:
            st.metric(
                "Travel Time (hrs)",
                travel_time
            )

    if st.button(
        "Predict Price"
    ):

        if distance is None:

            st.error(
                "Selected route not found."
            )

        else:

            payload = {
                "distance": distance,
                "time": travel_time,
                "month": month,
                "flightType": flight_type,
                "agency": agency,
                "from": origin,
                "to": destination
            }

            response = requests.post(
                f"{API_BASE_URL}/predict_price",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:

                result = response.json()

                if "predicted_price" in result:

                    st.success(
                        f"Predicted Flight Price: ₹ {result['predicted_price']}"
                    )

                else:

                    st.error(
                        result
                    )

            else:

                st.error(
                    f"API Error: {response.status_code}"
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
            f"{API_BASE_URL}/predict_gender",
            json=payload,
            timeout=15
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
            f"{API_BASE_URL}/recommend_hotel",
            json=payload,
            timeout=15
        )

        result = pd.DataFrame(
            response.json()
        )

        st.dataframe(
            result
        )
