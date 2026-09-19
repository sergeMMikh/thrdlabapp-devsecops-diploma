FROM python:3.12-alpine3.24 AS dependencies

WORKDIR /build
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --only-binary=:all: -r requirements.txt \
    && /opt/venv/bin/python -m pip uninstall -y pip

FROM python:3.12-alpine3.24 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apk upgrade --no-cache \
    && /usr/local/bin/python -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.12/ensurepip \
    && addgroup -S django && adduser -S -G django django

COPY --from=dependencies /opt/venv /opt/venv
COPY --chown=django:django . .

USER django

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 8000), 2).close()"

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
