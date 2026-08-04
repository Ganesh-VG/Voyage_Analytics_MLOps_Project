# Voyage Analytics Streamlit Frontend

This folder contains the browser-based frontend for the Voyage Analytics API. It provides a polished travel dashboard with flight-price prediction, gender classification, and hotel recommendation screens.

## Dashboard features

- A branded landing panel and sidebar navigation.
- Route-aware flight inputs with average distance and duration context.
- Grouped, responsive forms and loading states for every API request.
- Clear API-health feedback before the dashboard is shown.
- Hotel recommendation summary metrics and a formatted recommendation table.

## API connection

The frontend reads `VOYAGE_API_BASE_URL` to locate the Flask API.

- When the variable is set, Streamlit calls that URL directly.
- When it is unset on a host machine, Streamlit uses `http://localhost:8000`, verifies health, and attempts to create a local `kubectl port-forward` to the Kubernetes API Service.
- In Kubernetes, `streamlit-configmap.yaml` sets the URL to `http://voyage-api-service:8000`. Kubernetes Service DNS then routes requests across the API replicas.

## Run locally

The frontend attempts the port-forward automatically. If its API health check fails, run the API port-forward manually:

```bash
kubectl port-forward -n voyage-analytics service/voyage-api-service 8000:8000
```

In another terminal at the repository root:

```bash
streamlit run streamlit_app/streamlit_app.py
```

## Build the frontend image

The image includes `data/processed/flight_user.csv`, which must exist before building it. Run preprocessing or the Airflow pipeline first.

```bash
docker build -f streamlit_app/Dockerfile -t voyage-streamlit:latest .
minikube image load --overwrite voyage-streamlit:latest
```

## Kubernetes deployment

The Kubernetes resources are in `../kubernetes/`:

- `streamlit-configmap.yaml`
- `streamlit-deployment.yaml`
- `streamlit-service.yaml`

Deploy them with the remaining project manifests:

```bash
kubectl apply -f kubernetes/
kubectl rollout status deployment/voyage-streamlit -n voyage-analytics
```

For Minikube on Windows, access the frontend through a Service tunnel:

```bash
minikube service voyage-streamlit-service -n voyage-analytics
```
