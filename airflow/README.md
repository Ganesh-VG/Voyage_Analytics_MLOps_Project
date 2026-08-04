# Voyage Analytics Airflow Pipeline

This folder configures Apache Airflow to orchestrate the Voyage Analytics machine-learning workflow. Airflow preprocesses source data, trains the models, and validates the generated artifacts before Jenkins builds and deploys the API and Streamlit frontend.

## Workflow

The DAG in [`dags/travel_pipeline_dag.py`](dags/travel_pipeline_dag.py) runs the following tasks:

```text
Preprocess raw travel data
  → Train flight-price model
  → Train gender-classification model
  → Build hotel-recommendation artifact
  → Validate model artifacts
```

The DAG ID is `travel_pipeline`. It has a daily schedule, with catchup disabled, and Jenkins can also trigger it through the Airflow REST API.

## Folder contents

| File or folder | Purpose |
| --- | --- |
| `Dockerfile` | Builds a custom Airflow 2.10.5 / Python 3.11 image with the project Python dependencies. |
| `requirements.txt` | Lists packages needed by the DAG and ML training scripts. |
| `docker-compose.yaml` | Starts PostgreSQL, initializes Airflow, and runs the webserver and scheduler. |
| `dags/travel_pipeline_dag.py` | Defines the preprocessing, model-training, and validation workflow. |
| `logs/` | Created at runtime to persist Airflow task logs. |
| `plugins/` | Optional runtime mount point for custom Airflow plugins; no custom plugins are currently included. |
| `config/` | Optional runtime mount point for additional Airflow configuration; no extra configuration files are currently included. |

## Services

```text
PostgreSQL
  ↑
Airflow initialization
  ↓
Airflow webserver + Airflow scheduler
```

| Service | Role |
| --- | --- |
| `postgres` | Stores Airflow metadata: DAG runs, task state, users, schedules, and configuration. Its data is retained in the named `postgres-db-volume`. |
| `airflow-init` | Migrates the Airflow database and creates the initial administrator account. It must finish successfully before the other Airflow services start. |
| `airflow-webserver` | Provides the Airflow UI and REST API on port `8080`. Jenkins calls this API to trigger the pipeline. |
| `airflow-scheduler` | Determines when DAG tasks should run and advances the workflow after each successful task. |

All Airflow services use `LocalExecutor`, which runs tasks locally and is appropriate for this local development setup.

## Prerequisites

- Docker Desktop running
- The shared project workspace path configured in `docker-compose.yaml` must exist
- Jenkins workspace synchronization configured if Jenkins will trigger the DAG

## Start Airflow

From this folder:

```bash
docker compose up --build -d
```

Check that the services are healthy:

```bash
docker compose ps
```

Open the Airflow UI at:

```text
http://localhost:8080
```

The initial local-development credentials configured by this project are:

```text
Username: admin
Password: admin
```

Do not use these credentials for a real deployment. Store production credentials in a secrets manager or Airflow/Kubernetes Secrets.

## Shared workspace

The Compose file mounts this host folder into every Airflow container:

```text
C:/Projects/JenkinsWorkspace/Voyage_Analytics_MLOps:/workspace
```

The DAG sets `PROJECT_ROOT = "/workspace"` and executes project scripts from that path. Jenkins copies the selected repository revision into the shared workspace before triggering Airflow, so the following data flow is possible:

```text
Jenkins checkout
  → shared host workspace
  → /workspace inside Airflow
  → processed data and trained models written to the shared project
  → Jenkins builds the API image with the new models
```

Update the Windows host path in `docker-compose.yaml` if the project is stored elsewhere.

## Build outputs for deployment

After a successful DAG run, Jenkins uses the shared workspace to build two deployable images:

- `voyage-api:latest`, which packages the validated model artifacts from `models/`.
- `voyage-streamlit:latest`, which packages the frontend and `data/processed/flight_user.csv` used for its interactive inputs.

Both images are then loaded into Minikube and deployed through the Kubernetes manifests.

## Run the DAG

### From the Airflow UI

1. Open **DAGs** at `http://localhost:8080`.
2. Find `travel_pipeline`.
3. Unpause it if necessary.
4. Select the play button and choose **Trigger DAG**.

### From the Airflow REST API

```bash
curl -u admin:admin -H "Content-Type: application/json" -X POST \
  http://localhost:8080/api/v1/dags/travel_pipeline/dagRuns \
  -d '{}'
```

Jenkins uses the same API endpoint, then polls the DAG-run state before it starts the Docker/Kubernetes deployment stages.

## View logs and diagnose failures

```bash
docker compose logs airflow-webserver
docker compose logs airflow-scheduler
docker compose logs airflow-init
```

Task logs are also available from the Airflow UI. If a training script fails, its Airflow task fails because the DAG runs scripts with `subprocess.run(..., check=True)`. Dependent tasks will not run.

## Stop Airflow

```bash
docker compose down
```

This stops the containers but preserves the PostgreSQL named volume. To remove the database data as well:

```bash
docker compose down -v
```

The second command removes local Airflow metadata and is intended only when you want a fresh setup.
