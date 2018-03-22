FROM nginx:1.13-alpine

MAINTAINER BP GREYLING

RUN apk add --no-cache openssl

# Setup NGINX configfiles
COPY nginx.conf             /etc/nginx/nginx.conf
COPY nginx.vh.default.conf  /etc/nginx/conf.d/default.conf
COPY uwsgi_params.conf      /etc/nginx/uwsgi/uwsgi_params.conf
COPY ssl-params.conf        /etc/nginx/snippets/ssl-params.conf

EXPOSE 80
RUN mkdir /etc/nginx/ssl
RUN touch /etc/nginx/ssl/nginx.key && touch /etc/nginx/ssl/nginx.crt
# Generate self-signed cert if needed
RUN  openssl req -x509 -newkey rsa:2048 \
         -keyout /etc/nginx/ssl/nginx.key -nodes \
         -out /etc/nginx/ssl/nginx.crt \
         -days 3650 -subj "/CN=localhost"

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]
