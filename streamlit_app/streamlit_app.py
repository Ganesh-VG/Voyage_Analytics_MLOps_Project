import os
import subprocess
import time
from calendar import month_name

import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "VOYAGE_API_BASE_URL",
    "http://localhost:8000"
).rstrip("/")

HOTEL_DESTINATIONS = [
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


def api_is_healthy():
    """Return whether the configured API health endpoint responds."""

    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


@st.cache_resource
def ensure_api_connection():
    """Use the configured API or create a local Minikube port-forward."""

    if api_is_healthy():
        return True, "Connected to the Voyage API"

    # A custom URL may belong to an API outside Minikube.
    if os.getenv("VOYAGE_API_BASE_URL"):
        return False, f"Cannot reach the configured API at {API_BASE_URL}."

    try:
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        subprocess.Popen(
            [
                "kubectl",
                "port-forward",
                "-n",
                "voyage-analytics",
                "service/voyage-api-service",
                "8000:8000"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags
        )
    except OSError as error:
        return False, f"Could not start the Kubernetes API tunnel: {error}"

    for _ in range(10):
        time.sleep(1)
        if api_is_healthy():
            return True, "Connected to the Voyage API through Minikube"

    return False, (
        "The Voyage API is unavailable. Start Minikube and confirm that "
        "voyage-api-service is running in the voyage-analytics namespace."
    )


@st.cache_data(show_spinner=False)
def load_flight_data():
    """Load the data used to populate interactive frontend controls."""

    return pd.read_csv("./data/processed/flight_user.csv")


def post_to_api(endpoint, payload):
    """Send a request to the API and return either JSON data or an error."""

    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as error:
        return None, f"Unable to reach the API: {error}"
    except ValueError:
        return None, "The API returned an invalid response."

    if isinstance(result, dict) and "error" in result:
        return None, result["error"]

    return result, None


def inject_styles():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #f7f9ff 0%, #ffffff 42%);
            }
            [data-testid="stSidebar"] {
                background: #101c37;
            }
            [data-testid="stSidebar"] * {
                color: #f7f9ff;
            }
            [data-testid="stSidebar"] .stRadio label {
                border-radius: 10px;
                padding: 0.25rem 0.35rem;
            }
            .hero {
                background: linear-gradient(120deg, #102b68, #1b6cd8 58%, #4aa6f2);
                border-radius: 22px;
                color: white;
                margin: 0.25rem 0 1.75rem;
                padding: 2.2rem 2.4rem;
                box-shadow: 0 16px 32px rgba(22, 78, 158, 0.20);
            }
            .hero h1 {
                color: white;
                font-size: 2.3rem;
                line-height: 1.15;
                margin: 0;
            }
            .hero p {
                color: #e7f2ff;
                font-size: 1.05rem;
                margin: 0.75rem 0 0;
            }
            .eyebrow {
                color: #78c9ff;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.11em;
                text-transform: uppercase;
            }
            .section-title {
                color: #14213d;
                font-size: 1.65rem;
                font-weight: 700;
                margin: 0.15rem 0;
            }
            .section-subtitle {
                color: #64748b;
                margin-bottom: 1.25rem;
            }
            div[data-testid="stMetric"] {
                background: white;
                border: 1px solid #e6edf8;
                border-radius: 14px;
                box-shadow: 0 6px 18px rgba(15, 40, 87, 0.06);
                padding: 0.85rem 1rem;
            }
            .result-card {
                background: #edf8f2;
                border: 1px solid #b8e5cb;
                border-radius: 16px;
                color: #14532d;
                margin-top: 1rem;
                padding: 1.1rem 1.25rem;
            }
            .result-card h3 {
                color: #166534;
                margin: 0 0 0.2rem;
            }
            .stButton > button {
                background: linear-gradient(120deg, #1558b0, #227ad9);
                border: 0;
                border-radius: 10px;
                color: white;
                font-weight: 700;
                min-height: 2.65rem;
                width: 100%;
            }
            .stButton > button:hover {
                background: linear-gradient(120deg, #124892, #1968bd);
                color: white;
            }
            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid #e6edf8;
                border-radius: 18px;
                padding: 0.65rem 1rem 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_flight_price_page(flight_df):
    st.markdown('<div class="eyebrow">Route intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Flight price prediction</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Choose a route and travel details to estimate the expected ticket price.</div>',
        unsafe_allow_html=True
    )

    with st.form("flight_price_form"):
        first_col, second_col = st.columns(2)

        with first_col:
            origin = st.selectbox("Departure city", sorted(flight_df["from"].unique()))
            agency = st.selectbox("Booking agency", sorted(flight_df["agency"].unique()))
            month = st.selectbox(
                "Travel month",
                range(1, 13),
                format_func=lambda value: month_name[value]
            )

        valid_destinations = sorted(
            flight_df.loc[flight_df["from"] == origin, "to"].unique()
        )

        with second_col:
            destination = st.selectbox("Arrival city", valid_destinations)
            flight_type = st.selectbox("Trip type", sorted(flight_df["flightType"].unique()))
            st.caption("Route details are calculated from historical trips.")

        submitted = st.form_submit_button("Estimate ticket price")

    route_data = flight_df[
        (flight_df["from"] == origin)
        & (flight_df["to"] == destination)
    ]

    distance = None
    travel_time = None

    if not route_data.empty:
        distance = round(float(route_data["distance"].mean()), 2)
        travel_time = round(float(route_data["time"].mean()), 2)

        distance_col, duration_col, route_col = st.columns([1, 1, 1.35])
        distance_col.metric("Average distance", f"{distance:,.0f} km")
        duration_col.metric("Average duration", f"{travel_time:.1f} hrs")
        route_col.metric("Selected route", f"{origin} to {destination}")

    if submitted:
        if distance is None:
            st.error("We could not find historical data for that route.")
            return

        payload = {
            "distance": distance,
            "time": travel_time,
            "month": month,
            "flightType": flight_type,
            "agency": agency,
            "from": origin,
            "to": destination
        }

        with st.spinner("Calculating your estimate..."):
            result, error = post_to_api("/predict_price", payload)

        if error:
            st.error(error)
            return

        price = result.get("predicted_price")
        if price is None:
            st.error("The API did not return a price prediction.")
            return

        st.markdown(
            f"""
            <div class="result-card">
                <h3>Estimated ticket price</h3>
                <div style="font-size: 2rem; font-weight: 800;">₹ {price:,.2f}</div>
                <div>Based on the selected route, month, agency, and trip type.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_gender_page(flight_df):
    st.markdown('<div class="eyebrow">Passenger insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Gender classification</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Provide traveller and booking details to receive a model classification.</div>',
        unsafe_allow_html=True
    )

    with st.form("gender_classification_form"):
        first_col, second_col = st.columns(2)

        with first_col:
            minimum_age = int(flight_df["age"].min())
            maximum_age = int(flight_df["age"].max())
            age = st.slider(
                "Traveller age",
                min_value=minimum_age,
                max_value=maximum_age,
                value=max(minimum_age, min(30, maximum_age))
            )
            company = st.selectbox("Company", sorted(flight_df["company"].unique()))
            flight_type = st.selectbox(
                "Trip type",
                sorted(flight_df["flightType"].unique()),
                key="gender_flight_type"
            )
            agency = st.selectbox(
                "Booking agency",
                sorted(flight_df["agency"].unique()),
                key="gender_agency"
            )

        with second_col:
            distance = st.number_input(
                "Distance (km)",
                min_value=float(flight_df["distance"].min()),
                max_value=float(flight_df["distance"].max()),
                value=float(flight_df["distance"].median()),
                step=1.0
            )
            travel_time = st.number_input(
                "Travel time (hrs)",
                min_value=float(flight_df["time"].min()),
                max_value=float(flight_df["time"].max()),
                value=float(flight_df["time"].median()),
                step=0.5
            )
            price = st.number_input(
                "Ticket price",
                min_value=float(flight_df["price"].min()),
                max_value=float(flight_df["price"].max()),
                value=float(flight_df["price"].median()),
                step=100.0
            )
            st.caption("Values are drawn from the historical travel dataset.")

        submitted = st.form_submit_button("Run classification")

    if submitted:
        payload = {
            "age": age,
            "company": company,
            "flightType": flight_type,
            "agency": agency,
            "distance": distance,
            "time": travel_time,
            "price": price
        }

        with st.spinner("Running classification..."):
            result, error = post_to_api("/predict_gender", payload)

        if error:
            st.error(error)
            return

        prediction = result.get("predicted_gender")
        if prediction is None:
            st.error("The API did not return a classification.")
            return

        st.markdown(
            f"""
            <div class="result-card">
                <h3>Classification result</h3>
                <div style="font-size: 2rem; font-weight: 800;">{prediction}</div>
                <div>This result is generated by the trained classification model.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_hotel_page():
    st.markdown('<div class="eyebrow">Stay discovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hotel recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Find popular stays using historic booking patterns for your destination.</div>',
        unsafe_allow_html=True
    )

    with st.form("hotel_recommendation_form"):
        destination = st.selectbox("Destination", HOTEL_DESTINATIONS)
        submitted = st.form_submit_button("Find recommended hotels")

    if not submitted:
        st.info("Select a destination to view the strongest hotel options.")
        return

    with st.spinner("Finding hotels..."):
        result, error = post_to_api(
            "/recommend_hotel",
            {"destination": destination}
        )

    if error:
        st.error(error)
        return

    recommendations = pd.DataFrame(result)
    if recommendations.empty:
        st.warning("No hotel recommendations are available for this destination.")
        return

    hotel_count = len(recommendations)
    average_price = recommendations["avg_price"].mean()
    booking_count = recommendations["booking_count"].sum()

    first_metric, second_metric, third_metric = st.columns(3)
    first_metric.metric("Recommended hotels", hotel_count)
    second_metric.metric("Total historic bookings", f"{booking_count:,.0f}")
    third_metric.metric("Average nightly price", f"₹ {average_price:,.2f}")

    display_columns = [
        "hotel_name",
        "booking_count",
        "avg_price",
        "avg_stay_days",
        "avg_total_spend"
    ]
    available_columns = [
        column for column in display_columns if column in recommendations.columns
    ]

    st.markdown("#### Recommended stays")
    st.dataframe(
        recommendations[available_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "hotel_name": "Hotel",
            "booking_count": st.column_config.NumberColumn("Bookings", format="%d"),
            "avg_price": st.column_config.NumberColumn("Average price", format="₹ %.2f"),
            "avg_stay_days": st.column_config.NumberColumn("Average stay", format="%.1f days"),
            "avg_total_spend": st.column_config.NumberColumn("Average spend", format="₹ %.2f")
        }
    )


st.set_page_config(
    page_title="Voyage Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles()
API_READY, API_STATUS = ensure_api_connection()

with st.sidebar:
    st.markdown("## ✈️ Voyage")
    st.caption("Travel intelligence platform")
    st.divider()
    menu = st.radio(
        "Explore",
        [
            "Flight price prediction",
            "Gender classification",
            "Hotel recommendations"
        ],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("SYSTEM STATUS")
    if API_READY:
        st.success("API online")
    else:
        st.error("API unavailable")

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Voyage Analytics</div>
        <h1>Make every trip a smarter decision.</h1>
        <p>Explore predictive travel insights, from flight estimates to hotel recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if not API_READY:
    st.error(API_STATUS)
    st.code(
        "kubectl port-forward -n voyage-analytics "
        "service/voyage-api-service 8000:8000"
    )
    st.stop()

try:
    flight_data = load_flight_data()
except (FileNotFoundError, pd.errors.ParserError) as error:
    st.error(f"Unable to load the travel dataset: {error}")
    st.stop()

if menu == "Flight price prediction":
    render_flight_price_page(flight_data)
elif menu == "Gender classification":
    render_gender_page(flight_data)
else:
    render_hotel_page()
