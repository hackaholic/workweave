FROM python:3.12-alpine

LABEL org.opencontainers.image.title="WorkWeave" \
      org.opencontainers.image.description="Multi-Agent Workflow & Task Coordination Dashboard" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WORKWEAVE_PORT=8088 \
    WORKWEAVE_DATA_DIR=/data \
    WORKWEAVE_PROJECTS_ROOT=/projects \
    WORKWEAVE_HOST=0.0.0.0

WORKDIR /app

# Create non-root system user matching typical host user (uid=1000)
RUN addgroup -g 1000 -S workweave && adduser -u 1000 -S workweave -G workweave

# Copy source code and install
COPY pyproject.toml README.md /app/
COPY workweave/ /app/workweave/

RUN pip install --no-cache-dir .

# Create workspace mount point
RUN mkdir -p /projects /data && chown -R workweave:workweave /app /projects /data

USER workweave

EXPOSE 8088

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8088/health || exit 1

ENTRYPOINT ["python", "-m", "workweave.cli"]
