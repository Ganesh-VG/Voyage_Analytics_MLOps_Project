# Voyage Analytics API

This folder contains the Flask application that serves Voyage Analytics machine-learning capabilities as HTTP endpoints. The service loads trained artifacts from the repository-level `models/` directory and is consumed by the Streamlit frontend through the Kubernetes `voyage-api-service`.

## Folder contents

| File | Purpose |
| --- | --- |
| `app.py` | Flask application, model/artifact loading, and prediction/recommendation routes. |
| `requirements.txt` | Python packages required to serve the API. |
| `Dockerfile` | Builds a deployable Python 3.11 image containing the API and model artifacts. |

## Prerequisites

- Python 3.11 or Docker
- Model artifacts generated in `../models/`

Required model artifacts include:

```text
flight_price_model.pkl
gender_classifier.pkl
hotel_recommendation.pkl
flight_columns.pkl
company_encoder.pkl
flight_encoder.pkl
agency_encoder.pkl
gender_encoder.pkl
```

Run the Airflow ML pipeline or the training scripts before starting a fresh API environment, so these artifacts exist.

## Run locally with Python

From the repository root:

```bash
pip install -r api/requirements.txt
python api/app.py
```

The server listens on `http://localhost:8000` by default. Set `PORT` to use another port:

```bash
export PORT=8001
python api/app.py
```

## Run with Docker

Build the image from the repository root, so Docker can copy both `api/` and `models/`:

```bash
docker build -f api/Dockerfile -t voyage-api:latest .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 voyage-api:latest
```

## Endpoints

### Health check

```http
GET /
```

Example response:

```json
{
  "message": "Voyage Analytics API Running Successfully"
}
```

Kubernetes uses this endpoint for readiness and liveness checks.

### Flight-price prediction

```http
POST /predict_price
Content-Type: application/json
```

Example request:

```json
{
  "distance": 500,
  "time": 1.5,
  "month": 8,
  "flightType": "RoundTrip",
  "agency": "Logtrip",
  "from": "New York",
  "to": "Boston"
}
```

Example response:

```json
{
  "predicted_price": 123.45
}
```

The API one-hot encodes categorical values and aligns the request features with the columns saved during model training.

### Gender classification

```http
POST /predict_gender
Content-Type: application/json
```

Example request:

```json
{
  "age": 30,
  "company": "Travel Company",
  "flightType": "RoundTrip",
  "agency": "Logtrip",
  "distance": 500,
  "time": 1.5,
  "price": 123.45
}
```

Example response:

```json
{
  "predicted_gender": "Female"
}
```

The categorical fields are transformed by the saved label encoders before the classifier makes a prediction.

### Hotel recommendation

```http
POST /recommend_hotel
Content-Type: application/json
```

Example request:

```json
{
  "destination": "Rio de Janeiro (RJ)"
}
```

The response is a JSON array of hotels in that destination, ranked from the precomputed recommendation artifact. It includes booking count, average price, average stay duration, and average spend.

## Test the health endpoint

With the API running locally:

```bash
curl http://localhost:8000/
```

## Deployment and frontend integration

Jenkins builds `voyage-api:latest` alongside `voyage-streamlit:latest`, loads both images into Minikube, and applies the manifests in `../kubernetes/`.

Within Kubernetes, the Streamlit frontend calls this API through:

```text
http://voyage-api-service:8000
```

The Service distributes requests across the available API Pods. To call the API directly from a host computer during local development:

```bash
kubectl port-forward -n voyage-analytics service/voyage-api-service 8000:8000
```

See [`../kubernetes/README.md`](../kubernetes/README.md) for deployment and frontend access instructions.

## Error responses

The prediction routes return an `error` field when loading data, transforming input, or making a prediction fails. Ensure the submitted categorical values were seen during model training and that all required JSON fields are present.
