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
# Hotel Recommendation Training
# ==================================================

def train_hotel_recommender():

    print("=" * 60)

    print("Hotel Recommendation Training Started")

    print("=" * 60)

    # ==========================================
    # Load Dataset
    # ==========================================

    hotel_user = pd.read_csv(

        os.path.join(

            DATA_DIR,

            "hotel_user.csv"

        )

    )

    print(

        f"Dataset Shape : {hotel_user.shape}"

    )

    print(

        f"Unique Destinations : {hotel_user['place'].nunique()}"

    )

    print(

        f"Unique Hotels : {hotel_user['hotel_name'].nunique()}"

    )

    # ==========================================
    # Create Recommendation Dataset
    # ==========================================

    hotel_recommendation_df = (

        hotel_user

        .groupby(

            [

                "place",

                "hotel_name"

            ]

        )

        .agg(

            booking_count=(

                "travelCode",

                "count"

            ),

            avg_price=(

                "price",

                "mean"

            ),

            avg_stay_days=(

                "days",

                "mean"

            ),

            avg_total_spend=(

                "total",

                "mean"

            )

        )

        .reset_index()

    )

    print(

        "Recommendation Dataset Created Successfully"

    )

    print(

        f"Recommendation Records : {len(hotel_recommendation_df)}"

    )

    print(

        hotel_recommendation_df.head()

    )

    # ==========================================
    # Sort Recommendations
    # ==========================================

    hotel_recommendation_df = hotel_recommendation_df.sort_values(

        by=[

            "place",

            "booking_count"

        ],

        ascending=[

            True,

            False

        ]

    )

    # ==========================================
    # Create Models Directory
    # ==========================================

    os.makedirs(

        MODELS_DIR,

        exist_ok=True

    )

    # ==========================================
    # Save Recommendation Artifact
    # ==========================================

    joblib.dump(

        hotel_recommendation_df,

        os.path.join(

            MODELS_DIR,

            "hotel_recommendation.pkl"

        )

    )

    print(

        "Hotel Recommendation Dataset Saved"

    )

    print("=" * 60)

    print("Hotel Recommendation Training Completed")

    print("=" * 60)


# ==================================================
# Run Script
# ==================================================

if __name__ == "__main__":

    train_hotel_recommender()