FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
RUN mkdir -p /app/data

CMD ["python", "app.py"]