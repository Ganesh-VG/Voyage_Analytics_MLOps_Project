# Voyage Analytics API

The API provides the project's machine-learning features: flight-price prediction, gender classification, and hotel recommendations.

## Folder contents

| Item | What it does |
| --- | --- |
| `app.py` | Starts the Flask API and defines the health, prediction, and recommendation endpoints. |
| `requirements.txt` | Lists the Python packages required to run the API. |
| `Dockerfile` | Builds a container containing the API and the repository's trained model files. |

## Before you start

From the repository root, make sure the trained files exist in `models/`. They are already included in this repository. To create fresh versions, run the Airflow pipeline described in [`../airflow/README.md`](../airflow/README.md).

You need either Python 3.11+ or Docker.

## Quick start with Python

Run these commands from the repository root:

```powershell
python -m pip install -r api/requirements.txt
python api/app.py
```

The API is ready at <http://localhost:8000>. Check it in a browser or run:

```powershell
curl http://localhost:8000/
```

## Quick start with Docker

Build from the repository root so Docker can include the model files:

```powershell
docker build -f api/Dockerfile -t voyage-api:latest .
docker run --rm -p 8000:8000 voyage-api:latest
```

## Available endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | `GET` | Check that the API is running. |
| `/predict_price` | `POST` | Estimate a flight price. |
| `/predict_gender` | `POST` | Run the gender-classification model. |
| `/recommend_hotel` | `POST` | List recommended hotels for a destination. |

Example flight-price request:

```powershell
curl -Method Post http://localhost:8000/predict_price `
  -ContentType 'application/json' `
  -Body '{"distance":500,"time":1.5,"month":8,"flightType":"RoundTrip","agency":"Logtrip","from":"New York","to":"Boston"}'
```

The accepted categories must match the training data. The Streamlit app supplies valid choices automatically.

## Use it with the frontend

Start this API first, then follow [`../streamlit_app/README.md`](../streamlit_app/README.md). The frontend uses `http://localhost:8000` by default.

For a Kubernetes deployment, see [`../kubernetes/README.md`](../kubernetes/README.md).
