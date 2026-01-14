# Инструкция по деплою с исправлениями ошибки 404 и Bad Gateway

## Проблема
При открытии страницы https://serv.temasuug.ru/ возникает ошибка 404 или Bad Gateway.

## Причины
1. Проблема была в неправильной конфигурации ingress маршрутов - отсутствовали пути для API, docs и redoc.
2. Также в конфигурации ingress использовались middleware, которые не существовали в кластере (например, "note-redirectscheme@kubernetescrd").

## Решение
Были внесены изменения в конфигурацию Helm чарта:

### 1. Обновлен файл `values.yaml`
- Добавлены пути для `/api`, `/docs` и `/redoc` в секцию `frontend.ingress.hosts.paths`

### 2. Обновлены шаблоны ingress:
- В `charts/notes-app/templates/ingress.yaml` удалена аннотация, ссылающаяся на несуществующий middleware
- В `charts/notes-app/templates/ingress-redirect.yaml` удалена аннотация, ссылающаяся на несуществующий middleware

### 3. Обновлен Dockerfile фронтенда
- Возвращена стандартная конфигурация nginx без использования шаблонов
- Убрана сложная логика с envsubst при запуске контейнера

### 4. Обновлена конфигурация nginx
- Возвращена стандартная конфигурация без прокси для API (маршрутизация теперь через ingress)

### 5. Обновлен deployment-frontend
- Убрана ненужная переменная окружения BACKEND_SERVICE_HOST

## Как обновить в CI/CD

1. Убедитесь, что в GitHub Actions workflow используется актуальная версия чарта
2. При деплое обязательно обновите ревизию Helm release:
   ```bash
   helm upgrade --install notes-app charts/notes-app -n note
   ```

3. Если изменения в ingress не применяются, возможно, потребуется удалить старые ingress-объекты вручную:
   ```bash
   kubectl delete ingress notes-app-ingress notes-app-ingress-http -n note
   helm upgrade --install notes-app charts/notes-app -n note
   ```

4. Используйте правильные теги образов, которые доступны в вашем репозитории:
   ```bash
   helm upgrade --install notes-app charts/notes-app \
     -n note \
     --set frontend.image.tag=[актуальный_тег] \
     --set backend.image.tag=[актуальный_тег]
   ```

5. После деплоя проверьте статус ingress:
   ```bash
   kubectl get ingress -n note
   ```

6. Проверьте, что все поды запустились корректно:
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
Если после обновления все равно возникают 404 ошибки или Bad Gateway:
1. Проверьте, что используете правильные теги образов в CI/CD
2. Убедитесь, что все поды запустились без ошибок
3. Проверьте логи Traefik на наличие ошибок middleware:
   ```bash
   kubectl logs -n kube-system deployment/traefik | grep -i error
   ```
4. Убедитесь, что в конфигурации ingress не осталось ссылок на несуществующие middleware
5. Проверьте TLS сертификаты, если используются

## DNS настройки
Если возникает ошибка DNS_PROBE_FINISHED_NXDOMAIN:
1. Убедитесь, что в DNS-зоне вашего домена (temasuug.ru) создана A-запись для subdomain
   serv.temasuug.ru, указывающая на IP-адрес, который отображается в ingress:
   ```bash
   kubectl get ingress -n note
   ```
   В данном случае, A-запись должна указывать на IP: 178.236.16.81
   
2. Также может потребоваться создание CNAME-записи, если вы используете CDN или облачные DNS-сервисы
   
Обратите внимание, что после изменения DNS-записей может потребоваться некоторое время (до 24 часов)
для распространения изменений по глобальной DNS-системе, хотя обычно это занимает от 5 до 30 минут.