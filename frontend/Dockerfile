FROM node:18-alpine AS build

WORKDIR /app

# Копирование package файлов и установка всех зависимостей (включая dev для сборки)
COPY package*.json ./
RUN npm ci --ignore-scripts

# Копирование исходного кода и сборка
COPY . .
RUN npm run build

FROM nginx:alpine

# Копирование собранных файлов
COPY --from=build /app/dist /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Удаление ненужных файлов для уменьшения размера
RUN rm -rf /usr/share/nginx/html/*.map

# Создание непривилегированного пользователя
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]