FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    influxdb-client==1.38.0 \
    requests==2.31.0

# Copy scripts
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.py

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variable for Python unbuffered output (logs appear immediately)
ENV PYTHONUNBUFFERED=1

# Default command runs the scheduler
CMD ["python3", "/app/scripts/scheduler.py"]
