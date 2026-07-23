FROM python:3.11-slim

WORKDIR /app

COPY api/ ./api/
COPY models/ ./models/

RUN pip install --no-cache-dir -r api/requirements.txt

EXPOSE 8000

CMD ["python", "api/app.py"]