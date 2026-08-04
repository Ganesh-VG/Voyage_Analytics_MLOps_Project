# Voyage Analytics MLOps Project

Voyage Analytics is an end-to-end machine-learning operations project for travel data. It preprocesses raw travel records, trains three machine-learning capabilities, tracks experiments, exposes predictions through a Flask API, presents them in Streamlit, and deploys the API to Minikube through Jenkins and Kubernetes.

## What it does

| Capability | Approach | Result |
| --- | --- | --- |
| Flight price prediction | Random Forest regression | Estimates a flight price from route, distance, duration, month, agency, and flight type. |
| Gender classification | Random Forest classification | Predicts a gender label from traveller and flight attributes. |
| Hotel recommendation | Aggregated recommendation table | Lists destination-specific hotels ranked by booking activity with price and stay statistics. |

## Architecture

```text
Raw CSV data
  -> preprocessing
  -> processed datasets
  -> Airflow training and validation pipeline
  -> model artifacts + MLflow tracking
  -> Flask API
  -> Docker image
  -> Minikube / Kubernetes

Jenkins coordinates Airflow, image creation, and Kubernetes deployment.
Streamlit calls the deployed Flask API for an interactive UI.
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
| `streamlit_app/` | Streamlit interface for the three capabilities. |
| `airflow/` | Airflow image, Docker Compose setup, and ML workflow DAG. |
| `jenkins/` | Custom Jenkins image, plugins, Compose setup, and CI/CD pipeline. |
| `kubernetes/` | Namespace, ConfigMap, Deployment, Service, and HPA manifests. |
| `scripts/` | Helper scripts, including Kubernetes deployment automation. |
| `mlflow/` | Local MLflow SQLite tracking database and run artifacts. |

## Requirements for a fresh clone

This project is developed for Windows with PowerShell, Docker Desktop, and Minikube. The ML/API portion can run on Windows, macOS, or Linux; adapt shell commands and any host-volume paths for your operating system.

### Required for the local ML pipeline and API

- Git
- Python 3.11 (the Docker images also use Python 3.11)
- `pip` and `venv`
- At least 8 GB RAM recommended, as the included datasets and Random Forest models are sizeable

Install the Python dependencies after cloning:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
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

```powershell
git --version
python --version
docker --version
docker compose version
minikube version
kubectl version --client
```

Start the local cluster before deploying:

```powershell
minikube start
kubectl config current-context
```

The expected Kubernetes context is `minikube`.

### Clone and configure

```powershell
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
6. Jenkins triggers that DAG, waits for success, builds `voyage-api:latest`, loads it into Minikube, and applies Kubernetes resources.
7. Kubernetes runs the Flask API with health checks and CPU-based autoscaling.
8. Streamlit sends user requests to the API endpoints.

## Quick start: train locally

Create and activate a Python virtual environment, then install project dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run preprocessing, training, and validation from the repository root:

```powershell
python src/preprocessing/preprocessing.py
python src/model_training/train_flight_price_model.py
python src/model_training/train_gender_classifier.py
python src/model_training/train_hotel_recommender.py
python src/evaluation/model_evaluation.py
```

## Run the API and Streamlit UI

Start the Flask API:

```powershell
pip install -r api/requirements.txt
python api/app.py
```

In another terminal, start the UI from the repository root:

```powershell
streamlit run streamlit_app/streamlit_app.py
```

The API listens on `http://localhost:8000` by default. The Streamlit app sends requests to that address.

Test the API health endpoint:

```powershell
Invoke-RestMethod http://localhost:8000/
```

## Airflow orchestration

Start Airflow from its folder:

```powershell
cd airflow
docker compose up --build -d
```

Open Airflow at `http://localhost:8080`, then trigger the `travel_pipeline` DAG. See [airflow/README.md](airflow/README.md) for service details and the workspace setup.

## Kubernetes deployment

With Docker, Minikube, and `kubectl` configured:

```powershell
docker build -f api/Dockerfile -t voyage-api:latest .
minikube image load voyage-api:latest
kubectl apply -f kubernetes/
kubectl rollout status deployment/voyage-api -n voyage-analytics
```

The NodePort Service exposes the API on port `30080`. See [kubernetes/README.md](kubernetes/README.md) for verification and cleanup commands.

## Jenkins CI/CD

Start Jenkins from its folder:

```powershell
cd jenkins
docker compose up --build -d
```

Jenkins is available at `http://localhost:8081`. Configure a Pipeline job to use `jenkins/Jenkinsfile`. It will trigger Airflow, build and load the API image, deploy Kubernetes resources, and verify the rollout. See [jenkins/README.md](jenkins/README.md) for the complete setup.

## Component documentation

- [API guide](api/README.md)
- [Airflow guide](airflow/README.md)
- [Jenkins guide](jenkins/README.md)
- [Kubernetes guide](kubernetes/README.md)

## Local-development notes

- Several Docker Compose mounts use machine-specific Windows paths such as `C:/Projects/JenkinsWorkspace/Voyage_Analytics_MLOps`. Update them for your system.
- The Airflow and Jenkins examples use local development credentials. Replace hardcoded credentials with managed secrets before any real deployment.
- Kubernetes uses `imagePullPolicy: Never`, so the `voyage-api:latest` image must be loaded into Minikube before deployment.
- Generated data, model artifacts, MLflow runtime files, Airflow runtime folders, and local virtual environments are ignored by Git.
