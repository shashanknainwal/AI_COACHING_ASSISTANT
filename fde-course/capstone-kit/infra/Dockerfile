# Build from the repo root:  docker build -f infra/Dockerfile -t capstone .
# Run:  docker run --rm -p 8080:8080 -e ANTHROPIC_API_KEY capstone
#       curl -s localhost:8080/ask -H 'content-type: application/json' -d '{"question":"Where is QF-1002?"}'
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /srv

RUN pip install --no-cache-dir "anthropic>=1.13,<2"

COPY app/ app/

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz').status==200 else 1)"

# The key comes from the environment (a secret manager in the cloud), never from the image.
CMD ["python", "-m", "app.server"]
