FROM python:3.13-alpine

COPY app /app
COPY cronjobs /etc/crontabs/root

WORKDIR /app

EXPOSE 8000

RUN apk update && \
    apk add --no-cache gcc musl-dev linux-headers python3-dev libffi-dev dcron nano && \
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install uwsgi && \
    /venv/bin/pip install -r /app/requirements.txt && \
    adduser --disabled-password --no-create-home duser && \
    mkdir -p /var/log

ENV PATH="/scripts:/venv/bin:$PATH"



CMD sh -c "crond && echo APP_AMBIENT in Django is set to: \$APP_AMBIENT && \
    if [ \"\$APP_AMBIENT\" = \"production\" ]; then \
        su duser -c 'uwsgi --http :8000 --module project.wsgi --master --processes 4 --threads 2'; \
    else \
        su duser -c 'python manage.py runserver 0.0.0.0:8000'; \
    fi"
