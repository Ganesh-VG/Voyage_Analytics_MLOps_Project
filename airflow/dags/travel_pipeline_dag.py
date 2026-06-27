from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime

import subprocess
import os


# ==================================================
# Project Root
# ==================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)


# ==================================================
# Task Functions
# ==================================================

def preprocess_data():

    subprocess.run(
        [
            "python",
            os.path.join(
                PROJECT_ROOT,
                "src",
                "preprocessing",
                "preprocessing.py"
            )
        ],
        check=True
    )


def train_flight_price_model():

    subprocess.run(
        [
            "python",
            os.path.join(
                PROJECT_ROOT,
                "src",
                "model_training",
                "train_flight_price_model.py"
            )
        ],
        check=True
    )


def train_gender_classifier():

    subprocess.run(
        [
            "python",
            os.path.join(
                PROJECT_ROOT,
                "src",
                "model_training",
                "train_gender_classifier.py"
            )
        ],
        check=True
    )


def train_hotel_recommender():

    subprocess.run(
        [
            "python",
            os.path.join(
                PROJECT_ROOT,
                "src",
                "model_training",
                "train_hotel_recommender.py"
            )
        ],
        check=True
    )


def model_validation():

    subprocess.run(
        [
            "python",
            os.path.join(
                PROJECT_ROOT,
                "src",
                "evaluation",
                "model_evaluation.py"
            )
        ],
        check=True
    )


# ==================================================
# DAG Definition
# ==================================================

default_args = {

    "owner": "Ganesh",

    "depends_on_past": False

}


with DAG(

    dag_id="travel_pipeline",

    description="Voyage Analytics MLOps Pipeline",

    default_args=default_args,

    start_date=datetime(
        2026,
        1,
        1
    ),

    schedule="@daily",

    catchup=False,

    tags=[
        "mlops",
        "travel",
        "machine_learning"
    ]

) as dag:

    preprocess_task = PythonOperator(

        task_id="preprocess_data",

        python_callable=preprocess_data

    )


    flight_training_task = PythonOperator(

        task_id="train_flight_price_model",

        python_callable=train_flight_price_model

    )


    gender_training_task = PythonOperator(

        task_id="train_gender_classifier",

        python_callable=train_gender_classifier

    )


    hotel_training_task = PythonOperator(

        task_id="train_hotel_recommender",

        python_callable=train_hotel_recommender

    )


    validation_task = PythonOperator(

        task_id="model_validation",

        python_callable=model_validation

    )


    (
        preprocess_task
        >>
        flight_training_task
        >>
        gender_training_task
        >>
        hotel_training_task
        >>
        validation_task
    )