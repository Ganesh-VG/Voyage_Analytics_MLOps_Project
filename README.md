# Voyage Analytics MLOps Project

Voyage Analytics is an end-to-end machine-learning operations project for travel data. It preprocesses raw travel records, trains three machine-learning capabilities, tracks experiments, serves predictions with Flask, and deploys both the API and a Streamlit frontend to Minikube through Jenkins and Kubernetes.

## What it does

| Capability | Approach | Result |
| --- | --- | --- |
| Flight price prediction | Random Forest regression | Estimates a flight price from route, distance, duration, month, agency, and flight type. |
| Gender classification | Random Forest classification | Predicts a gender label from traveller and flight attributes. |
| Hotel recommendation | Aggregated recommendation table | Lists destination-specific hotels ranked by booking activity with price and stay statistics. |

## Architecture

```text
Raw CSV data -> preprocessing -> model training and validation -> model artifacts
                                      ^
                                      | Airflow orchestrates the ML workflow

Jenkins builds and deploys both application images:

Browser -> Streamlit Service -> Streamlit Pod -> voyage-api-service -> API Pods
                                                    (2 to 5 replicas)
```

## Repository layout

| Folder | Purpose |
| --- | --- |
| `data/raw/` | Source user, flight, and hotel CSV data. |
| `data/processed/` | Generated preprocessed datasets. |
| `src/preprocessing/` | Data cleaning, date feature engineering, and dataset joins. |
| `src/model_training/` | Flight-price, gender-classification, and hotel-recommendation training scripts. |
| `src/evaluation/` | Model-artifact validation script. |
| `models/` | Generated trained models, feature encoders, and feature-importance reports. |
| `notebooks/` | Exploratory analysis, modelling, MLflow, and evaluation notebooks. |
| `api/` | Flask model-serving API and container definition. |
| `streamlit_app/` | Streamlit interface, frontend Dockerfile, and frontend-specific dependencies. |
| `airflow/` | Airflow image, Docker Compose setup, and ML workflow DAG. |
| `jenkins/` | Custom Jenkins image, plugins, Compose setup, and CI/CD pipeline. |
| `kubernetes/` | API and frontend ConfigMaps, Deployments, Services, and API HPA manifests. |
| `mlflow/` | Local MLflow SQLite tracking database and run artifacts. |

## Requirements for a fresh clone

This project is documented for Git Bash on Windows with Docker Desktop and Minikube. The ML/API portion can run on Windows, macOS, or Linux; adapt shell commands and any host-volume paths for your operating system.

### Required for the local ML pipeline and API

- Git
- Python 3.11 (the Docker images also use Python 3.11)
- `pip` and `venv`
- At least 8 GB RAM recommended, as the included datasets and Random Forest models are sizeable

Install the Python dependencies after cloning:

```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install Flask pandas numpy scikit-learn scipy xgboost joblib mlflow matplotlib seaborn streamlit
```

The root `requirements.txt` also lists `apache-airflow`, but Airflow is run by this project inside its Docker image. Do not install Airflow directly in a Windows virtual environment; use the Compose setup in `airflow/` instead.

### Required for the full MLOps deployment

- Docker Desktop, running and configured to use Linux containers
- Docker Compose v2 (`docker compose version`)
- Minikube, with a running local cluster
- `kubectl`, configured to use the Minikube context
- Enough free disk space for Docker images, Minikube, PostgreSQL, Jenkins, and ML artifacts (20 GB recommended)

Verify the command-line tools:

```bash
git --version
python --version
docker --version
docker compose version
minikube version
kubectl version --client
```

Start the local cluster before deploying:

```bash
minikube start
kubectl config current-context
```

The expected Kubernetes context is `minikube`.

### Clone and configure

```bash
git clone <repository-url>
cd Voyage_Analytics_MLOps_Project
```

Before starting Airflow or Jenkins, update these host-specific bind mounts in their Compose files to point to your own shared workspace:

- `airflow/docker-compose.yaml`
- `jenkins/docker-compose.yaml`

Both files currently reference `C:/Projects/JenkinsWorkspace/Voyage_Analytics_MLOps`. Create that directory or replace the path consistently in both files. Jenkins copies the checked-out project there, and Airflow accesses it at `/workspace` to run the training scripts.

## End-to-end workflow

1. `preprocessing.py` reads the raw CSV files, removes duplicates, derives date features, and joins flight/hotel data with user data.
2. The model-training scripts create the model artifacts in `models/`.
3. The flight-price script records parameters, metrics, and artifacts in MLflow.
4. `model_evaluation.py` confirms models, encoders, and sample predictions load successfully.
5. Airflow runs this workflow as the `travel_pipeline` DAG, on a daily schedule or on demand.
6. Jenkins triggers that DAG, waits for success, and builds `voyage-api:latest` plus `voyage-streamlit:latest`.
7. Kubernetes runs the Flask API with health checks and CPU-based autoscaling.
8. Kubernetes runs Streamlit in a separate Pod; it calls `voyage-api-service` through cluster DNS.

## Quick start: train locally

Create and activate a Python virtual environment, then install project dependencies:

```bash
python -m venv venv
source venv/Scripts/activate
pip install Flask pandas numpy scikit-learn scipy xgboost joblib mlflow matplotlib seaborn streamlit
```

Run preprocessing, training, and validation from the repository root:

```bash
python src/preprocessing/preprocessing.py
python src/model_training/train_flight_price_model.py
python src/model_training/train_gender_classifier.py
python src/model_training/train_hotel_recommender.py
python src/evaluation/model_evaluation.py
```

## Run the API and Streamlit UI

Start the Flask API:

```bash
pip install -r api/requirements.txt
python api/app.py
```

In another terminal, start the UI from the repository root:

```bash
streamlit run streamlit_app/streamlit_app.py
```

The API listens on `http://localhost:8000` by default. The frontend checks API health before showing the dashboard. When `VOYAGE_API_BASE_URL` is not set, it can create a local Kubernetes port-forward automatically; if that is unavailable, run the following command in another terminal:

```bash
kubectl port-forward -n voyage-analytics service/voyage-api-service 8000:8000
```

Test the API health endpoint:

```bash
curl http://localhost:8000/
```

## Airflow orchestration

Start Airflow from its folder:

```bash
cd airflow
docker compose up --build -d
```

Open Airflow at `http://localhost:8080`, then trigger the `travel_pipeline` DAG. See [airflow/README.md](airflow/README.md) for service details and the workspace setup.

## Kubernetes deployment

With Docker, Minikube, and `kubectl` configured:

```bash
docker build -f api/Dockerfile -t voyage-api:latest .
docker build -f streamlit_app/Dockerfile -t voyage-streamlit:latest .
minikube image load --overwrite voyage-api:latest
minikube image load --overwrite voyage-streamlit:latest
kubectl apply -f kubernetes/
kubectl rollout restart deployment/voyage-api -n voyage-analytics
kubectl rollout restart deployment/voyage-streamlit -n voyage-analytics
kubectl rollout status deployment/voyage-api -n voyage-analytics
kubectl rollout status deployment/voyage-streamlit -n voyage-analytics
```

The frontend is exposed by `voyage-streamlit-service`. For Minikube on Windows, run `minikube service voyage-streamlit-service -n voyage-analytics` to open it. See [kubernetes/README.md](kubernetes/README.md) for verification and cleanup commands.

## Jenkins CI/CD

Start Jenkins from its folder:

```bash
cd jenkins
docker compose up --build -d
```

Jenkins is available at `http://localhost:8081`. Configure a Pipeline job to use `jenkins/Jenkinsfile`. It triggers Airflow, builds and loads both application images, deploys Kubernetes resources, and verifies both rollouts. See [jenkins/README.md](jenkins/README.md) for the complete setup.

## Start the complete project

Run these commands from Git Bash at the repository root. The normal automated path is to start the platform services, then use the Jenkins Pipeline to train and deploy the application.

### First-time setup from a fresh clone

Clone the repository and enter it:

```bash
git clone <repository-url>
cd Voyage_Analytics_MLOps_Project
```

Create a local Python environment for notebooks, local training, and local Streamlit use:

```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install Flask pandas numpy scikit-learn scipy xgboost joblib mlflow matplotlib seaborn streamlit
```

Before continuing, start Docker Desktop manually and wait until it reports that the Docker engine is running. Then update the host-specific workspace paths in both files so Jenkins and Airflow share the same directory:

- `airflow/docker-compose.yaml`
- `jenkins/docker-compose.yaml`

The current example path is `C:/Projects/JenkinsWorkspace/Voyage_Analytics_MLOps`. Create that directory or replace it consistently in both files.

### 1. Start Minikube

```bash
minikube start
kubectl config current-context
```

The expected context is `minikube`.

### 2. Start Airflow

```bash
docker compose -f airflow/docker-compose.yaml up --build -d
docker compose -f airflow/docker-compose.yaml ps
```

Open Airflow at `http://localhost:8080`.

### 3. Start Jenkins

```bash
docker compose -f jenkins/docker-compose.yaml up --build -d
docker compose -f jenkins/docker-compose.yaml ps
```

Open Jenkins at `http://localhost:8081`, then run the configured Pipeline job. Jenkins triggers the Airflow DAG, builds both application images, loads them into Minikube, and deploys the API and frontend.

### 4. Use the deployed frontend

After the Pipeline succeeds, verify the application Pods:

```bash
kubectl get pods -n voyage-analytics
```

Open the Streamlit frontend:

```bash
minikube service voyage-streamlit-service -n voyage-analytics
```

Keep this command running while using the local Minikube service tunnel. Press `Ctrl+C` when you are finished with the tunnel.

### Manual deployment alternative

If you do not want to use Jenkins, first run the preprocessing and training commands in [Quick start: train locally](#quick-start-train-locally). Then build and deploy both images:

```bash
docker build -f api/Dockerfile -t voyage-api:latest .
docker build -f streamlit_app/Dockerfile -t voyage-streamlit:latest .
minikube image load --overwrite voyage-api:latest
minikube image load --overwrite voyage-streamlit:latest
kubectl apply -f kubernetes/
kubectl rollout restart deployment/voyage-api -n voyage-analytics
kubectl rollout restart deployment/voyage-streamlit -n voyage-analytics
kubectl rollout status deployment/voyage-api -n voyage-analytics
kubectl rollout status deployment/voyage-streamlit -n voyage-analytics
```

## Stop the complete project

Stop any active `minikube service` or `kubectl port-forward` command first with `Ctrl+C`. Then stop the platform services and Minikube:

```bash
docker compose -f airflow/docker-compose.yaml down
docker compose -f jenkins/docker-compose.yaml down
minikube stop
```

These commands preserve Docker volumes, Airflow metadata, Jenkins configuration, and Kubernetes resources. The next `minikube start` resumes the cluster and its deployed resources.

### Optional full project cleanup

The following commands remove the Docker and Minikube resources created for Voyage Analytics only. They do not run broad commands such as `docker system prune -a`, which could remove assets belonging to unrelated projects.

First remove the Kubernetes cluster, including its Minikube container and in-cluster images:

```bash
minikube delete -p minikube
```

Then remove the Airflow and Jenkins containers, networks, and persisted Compose volumes:

```bash
docker compose -f airflow/docker-compose.yaml down --volumes --remove-orphans
docker compose -f jenkins/docker-compose.yaml down --volumes --remove-orphans
```

Finally remove the locally built Voyage images:

```bash
docker image rm voyage-api:latest voyage-streamlit:latest
docker image rm airflow-airflow-webserver:latest airflow-airflow-scheduler:latest airflow-airflow-init:latest
docker image rm jenkins-jenkins:latest
```

Docker may report that an image does not exist or is still used by another container. In that case, inspect the relevant container first rather than force-removing it.

## Component documentation

- [API guide](api/README.md)
- [Airflow guide](airflow/README.md)
- [Jenkins guide](jenkins/README.md)
- [Kubernetes guide](kubernetes/README.md)
- [Streamlit frontend guide](streamlit_app/README.md)

## Local-development notes

- Several Docker Compose mounts use machine-specific Windows paths such as `C:/Projects/JenkinsWorkspace/Voyage_Analytics_MLOps`. Update them for your system.
- The Airflow and Jenkins examples use local development credentials. Replace hardcoded credentials with managed secrets before any real deployment.
- Kubernetes uses `imagePullPolicy: Never`, so both locally built images must be loaded into Minikube before deployment. Use `minikube image load --overwrite` when refreshing an existing image tag.
- Generated data, model artifacts, MLflow runtime files, Airflow runtime folders, and local virtual environments are ignored by Git.
