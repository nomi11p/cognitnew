FROM python:3.14-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Cloud Run provides PORT automatically
ENV PORT=8080

# Start Cognit
ENV PORT=8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT server:app"]