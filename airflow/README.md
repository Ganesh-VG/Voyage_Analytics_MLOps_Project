# Voyage Analytics Airflow Pipeline

Airflow runs the machine-learning workflow: prepare the data, train the three models, and validate the generated files.

## What you need

- Docker Desktop running
- This repository cloned locally
- A `shared-workspace` folder at the repository root (already present after cloning)

Airflow runs scripts from `shared-workspace`, not directly from this repository. Before your first run, copy the files needed by the training workflow into that folder. From the repository root in PowerShell:

```powershell
Copy-Item -Path .\data, .\models, .\src -Destination .\shared-workspace -Recurse -Force
```

Run this copy step again whenever you change project code and want Airflow to use those changes. Jenkins performs the same synchronization automatically during its pipeline.

## Start Airflow

From the `airflow` folder:

```powershell
docker compose up --build -d
docker compose ps
```

Open these pages:

| Service | Address | Sign in |
| --- | --- | --- |
| Airflow | <http://localhost:8080> | `admin` / `admin` |
| MLflow | <http://localhost:5000> | No sign-in |

The credentials are for local development only.

## Run the pipeline

1. Open Airflow and find the `travel_pipeline` DAG.
2. Turn it on if it is paused.
3. Select the play button, then **Trigger DAG**.
4. Open the DAG run to follow each task.

The tasks run in this order:

```text
preprocess_data → train_flight_price_model → train_gender_classifier
→ train_hotel_recommender → model_validation
```

When the run succeeds, updated data is in `shared-workspace/data/processed/` and model files are in `shared-workspace/models/`. Copy them back to the repository only if you intentionally want to keep the generated artifacts there; Jenkins uses the shared workspace directly for deployment.

## Useful commands

```powershell
# Follow scheduler output
docker compose logs -f airflow-scheduler

# Stop the services while keeping local Airflow and MLflow history
docker compose down
```

To completely reset local Airflow and MLflow data, run `docker compose down -v`. This permanently removes the Docker volumes.

## Next steps

- To inspect model runs, read [`../mlflow/README.md`](../mlflow/README.md).
- To automate training and deployment, read [`../jenkins/README.md`](../jenkins/README.md).
