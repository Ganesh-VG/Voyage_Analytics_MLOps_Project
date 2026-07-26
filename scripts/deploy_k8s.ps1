Write-Host ""
Write-Host "====================================="
Write-Host "Voyage Kubernetes Deployment Started"
Write-Host "====================================="
Write-Host ""

Write-Host "Step 1: Checking Minikube Status..."
minikube status

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Minikube is not running."
    exit 1
}

Write-Host ""
Write-Host "Step 2: Loading Docker Image into Minikube..."
minikube image load voyage-api:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to load Docker image."
    exit 1
}

Write-Host ""
Write-Host "Step 3: Applying Kubernetes YAML files..."
kubectl apply -f kubernetes/

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Kubernetes deployment failed."
    exit 1
}

Write-Host ""
Write-Host "Step 4: Waiting for Deployment..."
kubectl rollout status deployment/voyage-api -n voyage-analytics

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Deployment rollout failed."
    exit 1
}

Write-Host ""
Write-Host "Step 5: Verifying Deployment..."

kubectl get pods -n voyage-analytics
kubectl get svc -n voyage-analytics

Write-Host ""
Write-Host "====================================="
Write-Host "Deployment Completed Successfully!"
Write-Host "====================================="