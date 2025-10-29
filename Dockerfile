# Use official lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# Copy requirement first
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your Flask app and templates
COPY . .

# Expose port 8080 (Cloud Run uses 8080)
EXPOSE 8080

# Run Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
