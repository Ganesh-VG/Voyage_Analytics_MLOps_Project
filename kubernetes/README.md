# Voyage Analytics Kubernetes Deployment

This folder contains the Kubernetes manifests used to deploy the Voyage Analytics Flask API and Streamlit frontend to a Minikube cluster.

## Architecture

```text
Browser
  |
  v
Streamlit Service (NodePort 30081)
  |
  v
Streamlit Pod (port 8501)
  |
  v
Voyage API Service
  |
  v
Voyage API Pods (2 to 5 replicas, port 8000)
```

## Manifest files

| File | Purpose |
| --- | --- |
| `namespace.yaml` | Creates the `voyage-analytics` namespace, which keeps this application's resources grouped together. |
| `configmap.yaml` | Defines non-sensitive environment variables for the API: `FLASK_ENV`, `MODEL_PATH`, and `PORT`. |
| `deployment.yaml` | Runs the `voyage-api` container, keeps two replicas available, and defines resource limits and health probes. |
| `service.yaml` | Creates a stable NodePort endpoint that forwards requests to the API Pods. |
| `hpa.yaml` | Scales the API between two and five replicas when average CPU utilization exceeds 70%. |
| `streamlit-configmap.yaml` | Gives the frontend the internal `voyage-api-service` URL. |
| `streamlit-deployment.yaml` | Runs the `voyage-streamlit` frontend container. |
| `streamlit-service.yaml` | Exposes the frontend through NodePort `30081`. |

## Prerequisites

- Docker
- Minikube running locally
- `kubectl` configured to use the Minikube context
- Locally built images named `voyage-api:latest` and `voyage-streamlit:latest`

## Deploy locally

From the repository root, build both application images and load them into Minikube:

```bash
docker build -f api/Dockerfile -t voyage-api:latest .
docker build -f streamlit_app/Dockerfile -t voyage-streamlit:latest .
minikube image load --overwrite voyage-api:latest
minikube image load --overwrite voyage-streamlit:latest
```

Apply all manifests:

```bash
kubectl apply -f kubernetes/
kubectl rollout restart deployment/voyage-api -n voyage-analytics
kubectl rollout restart deployment/voyage-streamlit -n voyage-analytics
```

## Verify the deployment

```bash
kubectl get pods -n voyage-analytics
kubectl get svc -n voyage-analytics
kubectl get deployment -n voyage-analytics
kubectl get hpa -n voyage-analytics
```

Wait for the API to become ready:

```bash
kubectl rollout status deployment/voyage-api -n voyage-analytics
kubectl rollout status deployment/voyage-streamlit -n voyage-analytics
```

## Access the frontend and API

For Minikube with the Docker driver on Windows, open the frontend through a Minikube Service tunnel:

```bash
minikube service voyage-streamlit-service -n voyage-analytics
```

In Git Bash, use the same command:

```bash
minikube service voyage-streamlit-service -n voyage-analytics
```

To call the API directly from the host, create a port-forward:

```bash
kubectl port-forward -n voyage-analytics service/voyage-api-service 8000:8000
```

Then call `http://localhost:8000/`.

Expected response:

```json
{
  "message": "Voyage Analytics API Running Successfully"
}
```

## Important notes

- `imagePullPolicy: Never` means Minikube must already contain both images; Kubernetes will not pull them from an image registry. Use `minikube image load --overwrite` when replacing an existing `latest` image.
- The API listens on container port `8000`; the frontend listens on port `8501`.
- The ConfigMap does not contain secrets. Use a Kubernetes `Secret` for passwords, keys, or tokens.
- The Horizontal Pod Autoscaler needs Metrics Server to obtain CPU metrics. Minikube normally provides it, but it can be enabled with `minikube addons enable metrics-server` if needed.

## Remove the deployment

```bash
kubectl delete -f kubernetes/
```
