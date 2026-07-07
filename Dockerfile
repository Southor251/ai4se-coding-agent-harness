FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY tests ./tests
COPY demo ./demo
COPY config ./config
COPY README.md ./

RUN python -m pip install --no-cache-dir -e ".[dev]"

CMD ["python", "-m", "pytest", "-q"]
