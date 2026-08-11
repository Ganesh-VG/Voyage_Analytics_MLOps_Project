# Voyage Analytics MLflow Tracking

MLflow lets you view the flight-price model's training runs, including parameters, metrics, and saved model artifacts.

## Folder contents

| Item | What it does |
| --- | --- |
| `mlflow.db` | A local SQLite database containing existing MLflow experiment history. The Docker setup can use it to seed a new tracking volume. |
| `artifacts/` | Saved files from earlier MLflow runs, such as trained model packages and reports. |
| `README.md` | This guide. |

## Start MLflow

MLflow is included in the Airflow Docker setup. From the repository root, start only MLflow:

```powershell
docker compose -f airflow/docker-compose.yaml up --build -d mlflow
```

Open <http://localhost:5000>. Start the full Airflow stack instead if you also want to train models:

```powershell
docker compose -f airflow/docker-compose.yaml up --build -d
```

## View a training run

1. Run the `travel_pipeline` DAG in Airflow.
2. Open <http://localhost:5000>.
3. Select **Flight Price Prediction**.
4. Open a run to compare metrics, parameters, and artifacts.

Airflow sends its training results to the MLflow service automatically.

## Record a run from your computer

With MLflow running, use PowerShell from the repository root:

```powershell
$env:MLFLOW_TRACKING_URI = 'http://localhost:5000'
python src/model_training/train_flight_price_model.py
Remove-Item Env:MLFLOW_TRACKING_URI
```

## Stop or reset

```powershell
# Stop services and keep experiment history
docker compose -f airflow/docker-compose.yaml down

# Remove all local Airflow and MLflow Docker data
docker compose -f airflow/docker-compose.yaml down -v
```

Use the second command only when you want a clean local setup.
