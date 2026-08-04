# Voyage Analytics Jenkins CI/CD

This folder configures Jenkins as the CI/CD controller for Voyage Analytics. Jenkins triggers the Airflow machine-learning pipeline, packages the validated API/model artifacts and Streamlit frontend into separate Docker images, and deploys both images to Minikube.

## Pipeline overview

```text
Repository checkout
  → copy source to shared workspace
  → trigger Airflow travel_pipeline DAG
  → wait for preprocessing, training, and validation
  → build voyage-api:latest and voyage-streamlit:latest
  → load both images into Minikube
  → apply Kubernetes manifests
  → verify the rollout
```

The pipeline definition is in [`Jenkinsfile`](Jenkinsfile).

## Folder contents

| File or folder | Purpose |
| --- | --- |
| `Dockerfile` | Builds a Jenkins LTS image with Docker, Git, `curl`, `jq`, `kubectl`, Minikube, and the required Jenkins plugins. |
| `docker-compose.yaml` | Runs the Jenkins container locally and mounts persistent Jenkins data, Docker access, the shared workspace, and Minikube configuration. |
| `Jenkinsfile` | Defines the CI/CD stages: checkout, Airflow trigger, model-pipeline gate, Docker build, Minikube load, Kubernetes deployment, and verification. |
| `plugins.txt` | Lists Jenkins plugins installed during the custom Jenkins image build. |
| `kube/config` | Kubeconfig used by `kubectl` inside the Jenkins container to connect to Minikube. |
| `kube/cache/` | Automatically generated `kubectl` API-discovery and HTTP cache; it is not source configuration and can be recreated. |

## Installed Jenkins plugins

| Plugin | Why it is included |
| --- | --- |
| `docker-workflow` | Supports Docker operations from Jenkins Pipelines. |
| `workflow-aggregator` | Provides the core Jenkins Pipeline functionality. |
| `git` | Enables source checkout from Git repositories. |
| `github` | Provides GitHub integration. |
| `pipeline-stage-view` | Displays a build as named pipeline stages. |
| `blueocean` | Adds a visual pipeline interface. |

## Prerequisites

- Docker Desktop running
- Minikube running
- Kubernetes CLI (`kubectl`) configured for Minikube on the host
- Airflow running and reachable from Jenkins at `http://host.docker.internal:8080`
- The shared workspace path in `docker-compose.yaml` available on the host

## Start Jenkins

From this directory:

```bash
docker compose up --build -d
```

Open Jenkins at:

```text
http://localhost:8081
```

To retrieve the initial administrator password after first startup:

```bash
docker exec voyage_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Create the pipeline job

1. In Jenkins, select **New Item**.
2. Choose **Pipeline** and give the job a name such as `voyage-analytics`.
3. Under **Pipeline**, select **Pipeline script from SCM**.
4. Select **Git**, enter this repository URL, and choose the branch to build.
5. Set the script path to `jenkins/Jenkinsfile`.
6. Save, then select **Build Now**.

## What the Jenkinsfile does

The pipeline first checks out the selected source revision and copies it to `/workspace`. Airflow uses this shared workspace to run preprocessing, training, and validation. The generated model artifacts and `data/processed/flight_user.csv` are then available for the API and frontend image builds.

Jenkins calls the Airflow REST API to trigger the `travel_pipeline` DAG and polls it for up to 30 minutes. A failed DAG fails the Jenkins build; a successful DAG permits deployment to continue.

Next, Jenkins builds the API and frontend images:

```text
voyage-api:latest
voyage-streamlit:latest
```

It loads both images into Minikube and applies the manifests in `../kubernetes/`. It restarts `voyage-api` and `voyage-streamlit`, waits for both rollouts, and lists Pods, Services, and Deployments in the `voyage-analytics` namespace.

## Verify Jenkins access to Kubernetes

Run this inside the Jenkins container:

```bash
docker exec voyage_jenkins kubectl get nodes
docker exec voyage_jenkins kubectl get pods -n voyage-analytics
```

## Important local-setup notes

- `docker-compose.yaml` contains host-specific Windows paths. Update these paths if your repository, Jenkins workspace, or Minikube profile lives elsewhere.
- The Docker socket mount gives Jenkins significant access to the host Docker daemon. This is convenient for local development but should be carefully controlled in production.
- `kube/config` references Minikube client certificates and keys. Treat it as sensitive configuration; avoid committing real cluster credentials to a public repository.
- `kube/cache/` is generated data and is normally appropriate for `.gitignore`.
- The Pipeline expects locally loaded `voyage-api:latest` and `voyage-streamlit:latest` images. Both deployments use `imagePullPolicy: Never`, so Minikube must contain both images before rollout.

## Stop Jenkins

```bash
docker compose down
```

The named `jenkins_home` volume is retained, so Jenkins configuration and job history remain available when the service is started again.
