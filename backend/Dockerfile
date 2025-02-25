FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    USE_MOCK_WORKFLOW=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only environment file first for better layer caching
COPY environment.yml ./

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "workflow-forge", "/bin/bash", "-c"]

# Copy the rest of the application
COPY . .

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD conda run -n workflow-forge curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["conda", "run", "--no-capture-output", "-n", "workflow-forge", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 