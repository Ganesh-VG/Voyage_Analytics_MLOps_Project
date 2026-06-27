import pandas as pd
import os


def preprocess_data():

    print(
        "=" * 50
    )
    print(
        "Starting Data Preprocessing..."
    )
    print(
        "=" * 50
    )

    # ==========================================
    # Create Output Directory
    # ==========================================

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    # ==========================================
    # Load Raw Data
    # ==========================================

    users = pd.read_csv(
        "data/raw/users.csv"
    )

    flights = pd.read_csv(
        "data/raw/flights.csv"
    )

    hotels = pd.read_csv(
        "data/raw/hotels.csv"
    )

    print(
        "Datasets Loaded"
    )

    # ==========================================
    # Remove Duplicates
    # ==========================================

    users = users.drop_duplicates()

    flights = flights.drop_duplicates()

    hotels = hotels.drop_duplicates()

    print(
        "Duplicates Removed"
    )

    # ==========================================
    # Convert Dates
    # ==========================================

    flights["date"] = pd.to_datetime(
        flights["date"]
    )

    hotels["date"] = pd.to_datetime(
        hotels["date"]
    )

    # ==========================================
    # Flight Features
    # ==========================================

    flights["year"] = (
        flights["date"]
        .dt.year
    )

    flights["month"] = (
        flights["date"]
        .dt.month
    )

    flights["day"] = (
        flights["date"]
        .dt.day
    )

    flights["day_of_week"] = (
        flights["date"]
        .dt.day_name()
    )

    # ==========================================
    # Hotel Features
    # ==========================================

    hotels["booking_month"] = (
        hotels["date"]
        .dt.month
    )

    # ==========================================
    # Merge Datasets
    # ==========================================

    flight_user = flights.merge(
        users,
        left_on="userCode",
        right_on="code",
        how="left"
    )

    hotel_user = hotels.merge(
        users,
        left_on="userCode",
        right_on="code",
        how="left"
    )

    travel_data = flights.merge(
        hotels,
        on=[
            "travelCode",
            "userCode"
        ],
        how="inner",
        suffixes=(
            "_flight",
            "_hotel"
        )
    )

    # ==========================================
    # Rename Columns
    # ==========================================

    hotel_user.rename(
        columns={
            "name_x": "hotel_name",
            "name_y": "name"
        },
        inplace=True
    )

    # ==========================================
    # Save Processed Data
    # ==========================================

    flight_user.to_csv(
        "data/processed/flight_user.csv",
        index=False
    )

    hotel_user.to_csv(
        "data/processed/hotel_user.csv",
        index=False
    )

    travel_data.to_csv(
        "data/processed/travel_data.csv",
        index=False
    )

    print(
        "Processed Files Saved"
    )

    print(
        "=" * 50
    )
    print(
        "Preprocessing Completed"
    )
    print(
        "=" * 50
    )


if __name__ == "__main__":

    preprocess_data()