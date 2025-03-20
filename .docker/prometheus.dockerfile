FROM alpine:latest

RUN apk update && apk add --no-cache \
    bash \
    curl \
    ca-certificates \
    apache2-utils \
    && update-ca-certificates

RUN curl -L https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz -o /tmp/prometheus.tar.gz \
    && tar -xvzf /tmp/prometheus.tar.gz -C /opt/ \
    && rm /tmp/prometheus.tar.gz

RUN ln -s /opt/prometheus-2.46.0.linux-amd64/prometheus /usr/local/bin/prometheus \
    && ln -s /opt/prometheus-2.46.0.linux-amd64/promtool /usr/local/bin/promtool

COPY ./prometheus/prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

WORKDIR /etc/prometheus

ENTRYPOINT ["/usr/local/bin/prometheus", "--config.file=/etc/prometheus/prometheus.yml"]