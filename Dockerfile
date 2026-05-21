# 🟩 Use an official optimized lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set system environment paths inside the image container
WORKDIR /app

# Install system dependencies required for compilation tasks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy local requirements configuration maps into workspace
COPY requirements.txt .

# Install dependencies cleanly without checking system cache paths
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining local directory project layers inside the image
COPY . .

# Expose the network communication port Streamlit listens on natively
EXPOSE 8501

# Configure container health-monitoring settings
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# The deployment command to initialize the dashboard automatically on launch
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]