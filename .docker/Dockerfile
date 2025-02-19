FROM python:3.11.3-alpine3.18
LABEL mantainer="mmmatheus013gmail.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY djangoapp /djangoapp
COPY .docker/scripts /scripts

WORKDIR /djangoapp

EXPOSE 8000

RUN apk update && \
    apk add --no-cache gcc musl-dev linux-headers python3-dev libffi-dev && \
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install uwsgi && \
    /venv/bin/pip install -r /djangoapp/requirements.txt && \
    adduser --disabled-password --no-create-home duser && \
    chmod -R +x /scripts

ENV PATH="/scripts:/venv/bin:$PATH"

USER duser

CMD ["commands.sh"]