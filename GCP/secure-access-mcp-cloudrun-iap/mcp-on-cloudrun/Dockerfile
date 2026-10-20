FROM python:3.13-slim

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml .

# Install dependencies into system environment
RUN uv pip install --system -r pyproject.toml

# Copy application source
COPY server.py .

# Expose standard Cloud Run port
ENV PORT=8080
EXPOSE 8080

CMD ["python", "server.py"]
