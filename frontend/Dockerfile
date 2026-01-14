FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Удаление devDependencies для уменьшения размера конечного образа
RUN npm prune --production

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf.template

EXPOSE 80

# Создаем скрипт для замены переменных в шаблоне конфигурации nginx
RUN apk add --no-cache bash
RUN echo '#!/bin/bash\nenvsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf\necho "Starting nginx with config:"\ncat /etc/nginx/nginx.conf\nnginx -g "daemon off;"' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]