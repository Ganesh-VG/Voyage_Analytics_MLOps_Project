FROM python:3.11-slim

WORKDIR /app

COPY streamlit_app/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app/ ./streamlit_app/
COPY data/processed/flight_user.csv ./data/processed/flight_user.csv

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
