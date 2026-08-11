# Voyage Analytics Jenkins CI/CD

Jenkins automates the full local deployment: it copies the chosen repository revision to the shared workspace, runs the Airflow training pipeline, builds the API and frontend images, and deploys them to Minikube.

## Before you start

Complete these one-time setup steps:

1. Install and start Docker Desktop.
2. Install Minikube and `kubectl`, then run:

   ```powershell
   minikube start --driver=docker
   ```

3. Start Airflow using [`../airflow/README.md`](../airflow/README.md). Jenkins must be able to reach it at `http://host.docker.internal:8080`.
4. Ensure the repository-root `shared-workspace` folder exists. It is mounted into both Jenkins and Airflow.

## Start Jenkins

From the `jenkins` folder:

```powershell
docker compose up --build -d
```

Open <http://localhost:8081>. Retrieve the initial password with:

```powershell
docker exec voyage_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Finish Jenkins's first-run setup in the browser and create an administrator account.

## Give Jenkins access to Minikube

After Jenkins is running, run the included setup script from Git Bash or WSL at the repository root:

```bash
bash scripts/init-minikube.sh
```

It writes a Minikube configuration into `jenkins/kube/` and checks that the Jenkins container can run `kubectl get nodes`. Run it again if you recreate Minikube.

## Create and run the pipeline

1. In Jenkins, choose **New Item** → **Pipeline**.
2. Give the job a name, for example `voyage-analytics`.
3. Under **Pipeline**, choose **Pipeline script from SCM**.
4. Select **Git**, enter this repository URL, choose the branch, and set **Script Path** to `jenkins/Jenkinsfile`.
5. Save, then choose **Build Now**.

The build may take several minutes. A successful run ends with the app deployed in the `voyage-analytics` namespace.

## Verify the result

```powershell
kubectl get pods -n voyage-analytics
minikube service voyage-streamlit-service -n voyage-analytics
```

## Troubleshooting

- If the build cannot trigger Airflow, check <http://localhost:8080> and verify the `travel_pipeline` DAG is visible.
- If `kubectl` fails inside Jenkins, rerun `bash scripts/init-minikube.sh` after Minikube and Jenkins are both running.
- If a model task fails, open the task log in Airflow; Jenkins stops when the DAG reports failure.

## Stop Jenkins

```powershell
docker compose down
```

Jenkins jobs and settings are kept in its Docker volume, so they remain available next time you start it.
