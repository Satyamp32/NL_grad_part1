# Use official lightweight Python image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for compiling python packages if any
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install pre-compiled pillow wheel or general packages
RUN pip install --no-cache-dir pillow==12.2.0
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Configure Streamlit settings
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start Streamlit dashboard
ENTRYPOINT ["streamlit", "run", "src/dashboard.py"]
