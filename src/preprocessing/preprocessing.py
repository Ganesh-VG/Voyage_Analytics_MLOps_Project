import os
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

RAW_DATA_DIR = os.path.join(

    BASE_DIR,

    "data",

    "raw"

)

PROCESSED_DATA_DIR = os.path.join(

    BASE_DIR,

    "data",

    "processed"

)


# ==================================================
# Data Preprocessing
# ==================================================

def preprocess_data():

    print("=" * 60)

    print("Data Preprocessing Started")

    print("=" * 60)

    # ==========================================
    # Create Processed Directory
    # ==========================================

    os.makedirs(

        PROCESSED_DATA_DIR,

        exist_ok=True

    )

    # ==========================================
    # Load Raw Data
    # ==========================================

    users = pd.read_csv(

        os.path.join(

            RAW_DATA_DIR,

            "users.csv"

        )

    )

    flights = pd.read_csv(

        os.path.join(

            RAW_DATA_DIR,

            "flights.csv"

        )

    )

    hotels = pd.read_csv(

        os.path.join(

            RAW_DATA_DIR,

            "hotels.csv"

        )

    )

    print("Datasets Loaded")

    print(f"Users   : {users.shape}")

    print(f"Flights : {flights.shape}")

    print(f"Hotels  : {hotels.shape}")

    # ==========================================
    # Remove Duplicate Records
    # ==========================================

    users = users.drop_duplicates()

    flights = flights.drop_duplicates()

    hotels = hotels.drop_duplicates()

    print("Duplicate Records Removed")

    # ==========================================
    # Convert Date Columns
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
    # Merge User Information
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
    # Save Processed Files
    # ==========================================

    flight_user.to_csv(

        os.path.join(

            PROCESSED_DATA_DIR,

            "flight_user.csv"

        ),

        index=False

    )

    hotel_user.to_csv(

        os.path.join(

            PROCESSED_DATA_DIR,

            "hotel_user.csv"

        ),

        index=False

    )

    travel_data.to_csv(

        os.path.join(

            PROCESSED_DATA_DIR,

            "travel_data.csv"

        ),

        index=False

    )

    print("=" * 60)

    print("Processed Datasets Saved")

    print("=" * 60)

    print(f"Flight User : {flight_user.shape}")

    print(f"Hotel User  : {hotel_user.shape}")

    print(f"Travel Data : {travel_data.shape}")

    print("=" * 60)

    print("Data Preprocessing Completed Successfully")

    print("=" * 60)


# ==================================================
# Run Script
# ==================================================

if __name__ == "__main__":

    preprocess_data()