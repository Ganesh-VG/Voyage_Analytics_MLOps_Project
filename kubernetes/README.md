# Voyage Analytics on Kubernetes

These files deploy the Voyage API and Streamlit app to a local Minikube cluster.

## Folder contents

| File | What it does |
| --- | --- |
| `namespace.yaml` | Creates the `voyage-analytics` namespace used by every application resource. |
| `configmap.yaml` | Supplies non-secret API settings such as the API port. |
| `deployment.yaml` | Runs and health-checks the API Pods. |
| `service.yaml` | Gives the API a stable in-cluster address: `voyage-api-service`. |
| `hpa.yaml` | Scales the API from two to five Pods based on CPU use. |
| `streamlit-configmap.yaml` | Tells the frontend how to reach the API inside the cluster. |
| `streamlit-deployment.yaml` | Runs and health-checks the Streamlit frontend Pod. |
| `streamlit-service.yaml` | Exposes the frontend through a Minikube NodePort. |

## What you need

- Docker Desktop running
- [Minikube](https://minikube.sigs.k8s.io/) and `kubectl` installed
- The trained files in `models/` and `data/processed/flight_user.csv` (included in this repository)

Start Minikube from the repository root:

```powershell
minikube start --driver=docker
kubectl config use-context minikube
```

## Easiest deployment: use Jenkins

Jenkins builds the images, triggers model training, loads the images into Minikube, and applies these manifests. For the complete automated path, follow [`../jenkins/README.md`](../jenkins/README.md).

## Deploy manually

Run the following commands from the repository root. The manifests use image tags supplied by environment variables; the commands below use the tag `local`.

1. Build and load both images from the repository root:

   ```powershell
   docker build -f api/Dockerfile -t voyage-api:local .
   docker build -f streamlit_app/Dockerfile -t voyage-streamlit:local .
   minikube image load voyage-api:local
   minikube image load voyage-streamlit:local
   ```

2. Create rendered copies of the manifests and apply them:

   ```powershell
   $env:API_IMAGE_TAG = 'local'
   $env:STREAMLIT_IMAGE_TAG = 'local'
   New-Item -ItemType Directory -Path .k8s-rendered -Force | Out-Null
   Get-ChildItem kubernetes/*.yaml | ForEach-Object {
     $content = Get-Content $_.FullName -Raw
     $content = $content.Replace('${API_IMAGE_TAG}', $env:API_IMAGE_TAG)
     $content = $content.Replace('${STREAMLIT_IMAGE_TAG}', $env:STREAMLIT_IMAGE_TAG)
     Set-Content -Path ".k8s-rendered/$($_.Name)" -Value $content
   }
   kubectl apply -f .k8s-rendered/
   ```

3. Wait for both applications:

   ```powershell
   kubectl rollout status deployment/voyage-api -n voyage-analytics
   kubectl rollout status deployment/voyage-streamlit -n voyage-analytics
   ```

## Open the app

```powershell
minikube service voyage-streamlit-service -n voyage-analytics
```

To call the API directly:

```powershell
kubectl port-forward -n voyage-analytics service/voyage-api-service 8000:8000
```

Then visit <http://localhost:8000/>.

## Check status

```powershell
kubectl get pods,services,deployments -n voyage-analytics
```

The API starts with two replicas and can scale to five when CPU usage is high. If the autoscaler does not show metrics, run `minikube addons enable metrics-server`.

## Remove the application

```powershell
kubectl delete -f .k8s-rendered/
Remove-Item .k8s-rendered -Recurse -Force
```

This removes the application resources but leaves Minikube and Docker images intact.
