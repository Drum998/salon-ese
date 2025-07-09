FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p instance/backups app/static/uploads

# Add test command
RUN echo '#!/bin/sh\npython -m pytest "$@"' > /usr/local/bin/run-tests && \
    chmod +x /usr/local/bin/run-tests

# Expose the port
EXPOSE 5010

# Run the application
CMD ["python", "run.py"] 