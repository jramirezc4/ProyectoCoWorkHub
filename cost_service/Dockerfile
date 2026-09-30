FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cost_service ./cost_service

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "cost_service.app:app"]
