#!/bin/sh

mkdir -p /etc/prometheus
chmod -R 755 /etc/prometheus

BCRYPT_HASH=$(htpasswd -nbBC 10 "${PROMETHEUS_USERNAME}" "${PROMETHEUS_PASSWORD}" | cut -d ':' -f 2)

echo "basic_auth_users:" > /etc/prometheus/web.yml
echo "  ${PROMETHEUS_USERNAME}: ${BCRYPT_HASH}" >> /etc/prometheus/web.yml

# Start Prometheus
exec prometheus --config.file=/etc/prometheus/prometheus.yml --web.config.file=/etc/prometheus/web.yml