FROM nginx:latest
COPY ./deployment/master/config/nginx/nginx.conf /etc/nginx/nginx.conf