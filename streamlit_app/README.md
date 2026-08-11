# Voyage Analytics Streamlit App

This is the browser interface for the Voyage Analytics API. It offers flight-price predictions, gender classification, and hotel recommendations.

## Folder contents

| Item | What it does |
| --- | --- |
| `streamlit_app.py` | Starts the dashboard, renders the three feature pages, and sends requests to the API. |
| `requirements.txt` | Lists the Python packages required by the frontend. |
| `Dockerfile` | Builds a container for the frontend and includes the processed flight dataset. |
| `README.md` | This guide. |

## Before you start

You need Python 3.11+ and a running API. The simplest option is to start the API locally in a separate terminal:

```powershell
python -m pip install -r api/requirements.txt
python api/app.py
```

The frontend reads `data/processed/flight_user.csv`, which is included in the repository. Run the Airflow pipeline if you want to regenerate it.

## Start the app

From the repository root, in a new terminal:

```powershell
python -m pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/streamlit_app.py
```

Open the address printed by Streamlit (normally <http://localhost:8501>).

The app connects to `http://localhost:8000` by default. To use an API at another address:

```powershell
$env:VOYAGE_API_BASE_URL = 'http://your-api-host:8000'
streamlit run streamlit_app/streamlit_app.py
```

## Run with Kubernetes

Deploy the API and frontend using [`../kubernetes/README.md`](../kubernetes/README.md). In Kubernetes, the app automatically uses the internal API Service.

## Build the container image

From the repository root:

```powershell
docker build -f streamlit_app/Dockerfile -t voyage-streamlit:latest .
```

The Docker image includes the processed flight dataset needed by the interactive forms.
