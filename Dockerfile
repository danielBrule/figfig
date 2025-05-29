FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY .env .  # Optional for local config, but consider secrets mgmt in Azure

CMD ["python", "app/main.py"]
