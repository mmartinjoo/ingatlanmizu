FROM node:26.7.0-alpine
COPY ./deploy/proxy.conf /etc/nginx/nginx.conf
EXPOSE 80
