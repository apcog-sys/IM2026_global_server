# Global Server image (independent). No database inside.
# Build FROM THE PROJECT ROOT (needs the shared common/ package):
#   docker build -f global_server/Dockerfile -t im-global-server .
#
# Config DEFAULTS ship in global_server/variable_config.json; override via env /
# ConfigMap. Needs the CA reachable at startup (IM_CA_URL). MySQL is external.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/        ./common/
COPY global_server/ ./global_server/

EXPOSE 9000
CMD ["uvicorn", "global_server.main:app", "--host", "0.0.0.0", "--port", "9000"]
