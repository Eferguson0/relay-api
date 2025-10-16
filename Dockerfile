FROM python:3.11-slim-bookworm

WORKDIR /app

# Install UV using pip (no apt/curl needed)
RUN pip install --no-cache-dir uv

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