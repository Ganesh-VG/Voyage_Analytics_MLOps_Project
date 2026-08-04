# Voyage Analytics Kubernetes Deployment

This folder contains the Kubernetes manifests used to deploy the Voyage Analytics Flask API to a Minikube cluster.

## Architecture

```text
Client
  |
  v
NodePort Service (port 30080)
  |
  v
Voyage API Pods (2 to 5 replicas, port 8000)
  |
  +-- ConfigMap environment variables
  +-- Readiness and liveness checks
```

## Manifest files

| File | Purpose |
| --- | --- |
| `namespace.yaml` | Creates the `voyage-analytics` namespace, which keeps this application's resources grouped together. |
| `configmap.yaml` | Defines non-sensitive environment variables for the API: `FLASK_ENV`, `MODEL_PATH`, and `PORT`. |
| `deployment.yaml` | Runs the `voyage-api` container, keeps two replicas available, and defines resource limits and health probes. |
| `service.yaml` | Creates a stable NodePort endpoint that forwards requests to the API Pods. |
| `hpa.yaml` | Scales the API between two and five replicas when average CPU utilization exceeds 70%. |

## Prerequisites

- Docker
- Minikube running locally
- `kubectl` configured to use the Minikube context
- A locally built API image named `voyage-api:latest`

## Deploy locally

From the repository root, build the API image and load it into Minikube:

```powershell
docker build -f api/Dockerfile -t voyage-api:latest .
minikube image load voyage-api:latest
```

Apply all manifests:

```powershell
kubectl apply -f kubernetes/
```

## Verify the deployment

```powershell
kubectl get pods -n voyage-analytics
kubectl get svc -n voyage-analytics
kubectl get deployment -n voyage-analytics
kubectl get hpa -n voyage-analytics
```

Wait for the API to become ready:

```powershell
kubectl rollout status deployment/voyage-api -n voyage-analytics
```

## Access the API

The Service exposes the API on NodePort `30080`. Get the Minikube IP and call the health endpoint:

```powershell
$minikubeIp = minikube ip
Invoke-RestMethod "http://${minikubeIp}:30080/"
```

Expected response:

```json
{
  "message": "Voyage Analytics API Running Successfully"
}
```

## Important notes

- `imagePullPolicy: Never` means Minikube must already contain `voyage-api:latest`; Kubernetes will not pull it from an image registry.
- The API listens on container port `8000`; the Service exposes it through NodePort `30080`.
- The ConfigMap does not contain secrets. Use a Kubernetes `Secret` for passwords, keys, or tokens.
- The Horizontal Pod Autoscaler needs Metrics Server to obtain CPU metrics. Minikube normally provides it, but it can be enabled with `minikube addons enable metrics-server` if needed.

## Remove the deployment

```powershell
kubectl delete -f kubernetes/
```
