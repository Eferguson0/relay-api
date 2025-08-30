FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV and update PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:${PATH}" && \
    uv --version
ENV PATH="/root/.local/bin:${PATH}"

# Copy pyproject.toml and uv.lock first to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application
COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 