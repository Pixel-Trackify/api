FROM python:3.11.3-alpine3.18

COPY app /app

WORKDIR /app

EXPOSE 8000

RUN apk update && \
    apk add --no-cache gcc musl-dev linux-headers python3-dev libffi-dev && \
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install uwsgi && \
    /venv/bin/pip install -r /app/requirements.txt && \
    adduser --disabled-password --no-create-home duser

ENV PATH="/scripts:/venv/bin:$PATH"

USER duser

CMD ["sh", "-c", '#!/bin/sh\
                set -e\
                if [ "$#" -gt 0 ]; then\
                    echo "▶ Running command: $@"\
                    exec "$@"\
                else\
                    echo "⚠ No command provided. Exiting."\
                    exit 1\
                fi']