FROM python:3.13.1-alpine3.18

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

CMD ["sh", "-c", "echo APP_AMBIENT in Django is set to: $APP_AMBIENT && \
    if [ \"$APP_AMBIENT\" = \"production\" ]; then \
        uwsgi --http :8000 --module project.wsgi --master --processes 4 --threads 2; \
    else \
        python manage.py runserver 0.0.0.0:8000; \
    fi;"]