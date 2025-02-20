FROM nginx:alpine

COPY nginx/proxy.conf /tmp/nginx/proxy.conf
COPY nginx/proxy-ssl.conf /tmp/nginx/proxy-ssl.conf

CMD ["sh", "-c", "echo APP_AMBIENT is set to: $APP_AMBIENT && \
    if [ \"$APP_AMBIENT\" = \"production\" ]; then \
        envsubst '$$APP_DOMAIN' < /tmp/nginx/proxy-ssl.conf > /etc/nginx/conf.d/default.conf; \
    else \
        cp /tmp/nginx/proxy.conf /etc/nginx/conf.d/default.conf; \
    fi && \
    nginx -g 'daemon off;'"]