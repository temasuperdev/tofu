# Инструкция по деплою с исправлениями ошибки 404

## Проблема
При открытии страницы https://serv.temasuug.ru/ возникает ошибка 404.

## Причина
Проблема была в неправильной конфигурации ingress маршрутов - отсутствовали пути для API, docs и redoc.

## Решение
Были внесены изменения в конфигурацию Helm чарта:

### 1. Обновлен файл `values.yaml`
- Добавлены пути для `/api`, `/docs` и `/redoc` в секцию `frontend.ingress.hosts.paths`

### 2. Обновлен Dockerfile фронтенда
- Возвращена стандартная конфигурация nginx без использования шаблонов
- Убрана сложная логика с envsubst при запуске контейнера

### 3. Обновлена конфигурация nginx
- Возвращена стандартная конфигурация без прокси для API (маршрутизация теперь через ingress)

### 4. Обновлен deployment-frontend
- Убрана ненужная переменная окружения BACKEND_SERVICE_HOST

## Как обновить в CI/CD

1. Убедитесь, что в GitHub Actions workflow используется актуальная версия чарта
2. При деплое обязательно обновите ревизию Helm release:
   ```bash
   helm upgrade --install notes-app charts/notes-app -n note
   ```

3. Используйте правильные теги образов, которые доступны в вашем репозитории:
   ```bash
   helm upgrade --install notes-app charts/notes-app \
     -n note \
     --set frontend.image.tag=[актуальный_тег] \
     --set backend.image.tag=[актуальный_тег]
   ```

4. После деплоя проверьте статус ingress:
   ```bash
   kubectl get ingress -n note
   ```

5. Проверьте, что все поды запустились корректно:
   ```bash
   kubectl get pods -n note
   ```

## Проверка результата
1. Откройте https://serv.tamasuug.ru/ - должна загрузиться главная страница
2. Проверьте API endpoints:
   - https://serv.tamasuug.ru/api/v1
   - https://serv.tamasuug.ru/docs
   - https://serv.tamasuug.ru/redoc

## Возможные проблемы
Если после обновления все равно возникают 404 ошибки:
1. Проверьте, что используете правильные теги образов в CI/CD
2. Убедитесь, что все поды запустились без ошибок
3. Проверьте конфигурацию Traefik ingress controller
4. Проверьте TLS сертификаты, если используются