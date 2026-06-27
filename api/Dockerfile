FROM python:3.11-slim

WORKDIR /app

COPY api/app.py api/
COPY api/docker_requirements.txt .
COPY models models/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "api/app.py"]