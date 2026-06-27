import pandas as pd
import joblib
import os


def train_hotel_recommender():

    print("=" * 50)
    print("Training Hotel Recommendation Model")
    print("=" * 50)

    # ==========================================
    # Load Dataset
    # ==========================================

    hotel_user = pd.read_csv(
        "data/processed/hotel_user.csv"
    )

    print(
        "Dataset Shape:",
        hotel_user.shape
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
        "Recommendation Dataset Created"
    )

    print(
        hotel_recommendation_df.head()
    )

    # ==========================================
    # Save Model Artifact
    # ==========================================

    os.makedirs(
        "models",
        exist_ok=True
    )

    joblib.dump(
        hotel_recommendation_df,
        "models/hotel_recommendation.pkl"
    )

    print(
        "Hotel Recommendation Dataset Saved Successfully"
    )

    print("=" * 50)
    print("Hotel Recommendation Training Completed")
    print("=" * 50)


if __name__ == "__main__":

    train_hotel_recommender()