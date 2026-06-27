from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

import subprocess
import os
import sys


# ==================================================
# Project Root (Docker Container)
# ==================================================

PROJECT_ROOT = "/opt/airflow"


# ==================================================
# Helper Function
# ==================================================

def run_script(script_path):

    full_path = os.path.join(
        PROJECT_ROOT,
        script_path
    )

    print("=" * 60)
    print(f"Running: {full_path}")
    print("=" * 60)

    subprocess.run(
        [
            sys.executable,
            full_path
        ],
        check=True
    )


# ==================================================
# Task Functions
# ==================================================

def preprocess_data():

    run_script(
        "src/preprocessing/preprocessing.py"
    )


def train_flight_price_model():

    run_script(
        "src/model_training/train_flight_price_model.py"
    )


def train_gender_classifier():

    run_script(
        "src/model_training/train_gender_classifier.py"
    )


def train_hotel_recommender():

    run_script(
        "src/model_training/train_hotel_recommender.py"
    )


def model_validation():

    run_script(
        "src/evaluation/model_evaluation.py"
    )


# ==================================================
# Default Arguments
# ==================================================

default_args = {

    "owner": "Ganesh",

    "depends_on_past": False

}


# ==================================================
# DAG Definition
# ==================================================

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


    preprocess_task >> flight_training_task >> gender_training_task >> hotel_training_task >> validation_task