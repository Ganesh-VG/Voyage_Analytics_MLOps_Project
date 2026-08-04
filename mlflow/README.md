# Voyage Analytics MLflow Tracking

MLflow records the Flight Price Prediction training runs: model parameters, quality metrics, model files, feature columns, and feature-importance reports. It is integrated with the Airflow Compose stack and is available in a browser at `http://localhost:5000`.

## Start the MLflow UI

From the repository root, start only MLflow when you want to inspect experiments without starting all Airflow services:

```bash
docker compose -f airflow/docker-compose.yaml up --build -d mlflow
docker compose -f airflow/docker-compose.yaml ps mlflow
```

Open:

```text
http://localhost:5000
```

Starting the full Airflow stack also starts MLflow automatically:

```bash
docker compose -f airflow/docker-compose.yaml up --build -d
```

## Pipeline runs

The Airflow scheduler supplies `MLFLOW_TRACKING_URI=http://mlflow:5000` to the training workflow. When Jenkins triggers the `travel_pipeline` DAG, the Flight Price Prediction task creates or updates the **Flight Price Prediction** experiment in MLflow.

After a successful DAG run, open that experiment to compare run parameters and metrics or download logged artifacts.

## Track a local training run in the UI

If you run the training script directly on your computer, point it at the running service first:

```bash
docker compose -f airflow/docker-compose.yaml up --build -d mlflow
export MLFLOW_TRACKING_URI=http://localhost:5000
python src/model_training/train_flight_price_model.py
unset MLFLOW_TRACKING_URI
```

Without `MLFLOW_TRACKING_URI`, the script falls back to a local SQLite store under `mlflow/`. That fallback is useful for standalone work, but its results are not as durable as the Compose-managed tracking service.

## Data retention and cleanup

The active MLflow database and artifacts are kept in the `mlflow-data` named Docker volume. On its first start, the service copies any existing history in this repository's `mlflow/` folder into that volume, allowing the earlier Airflow-based artifact paths to remain readable.

Normal shutdown preserves MLflow history:

```bash
docker compose -f airflow/docker-compose.yaml down
```

The following full cleanup removes the MLflow volume together with Airflow's PostgreSQL data:

```bash
docker compose -f airflow/docker-compose.yaml down --volumes --remove-orphans
```

Use the cleanup command only when you intentionally want to remove local experiment history.
