FROM python:3.11-slim

LABEL "language"="python"
LABEL "framework"="flask"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir flask

EXPOSE 8080

CMD ["python", "app.py"]
