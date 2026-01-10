from flask import request, jsonify, render_template_string
from marshmallow import ValidationError
from datetime import datetime
import time
import logging
from ..utils.validators import MessageSchema
from ..services.message_service import MessageService
from ..config import get_config
from ..utils.logging_config import configure_logging
from ..utils.cache_manager import cache_manager

# Глобальные счетчики для метрик
request_count = 0
start_time = time.time()

# Настройка структурированного логирования
logger = configure_logging()

# Получение конфигурации
config = get_config()

# Сервис для работы с сообщениями
message_service = MessageService()

# HTML шаблон для главной страницы
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>K3s Demo App</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5; }
        .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #33; }
        .info { background-color: #e8f4f8; padding: 15px; border-left: 4px solid #00bcd4; margin: 20px 0; }
        code { background-color: #f0f0; padding: 2px 6px; border-radius: 3px; }
        .endpoint { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 4px; }
        .notes-section { background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 K3s CI/CD Demo Application</h1>
        <div class="info">
            <p><strong>Приложение успешно развернуто в K3s!</strong></p>
            <p>Версия: <code>{{ version }}</code></p>
            <p>Окружение: <code>{{ environment }}</code></p>
            <p>Pod: <code>{{ hostname }}</code></p>
            <p>Время запуска: <code>{{ timestamp }}</code></p>
        </div>
        
        <h2>📊 Доступные API endpoints:</h2>
        <div class="endpoint">
            <code>GET /api/health</code> - Health check
        </div>
        <div class="endpoint">
            <code>GET /api/info</code> - Информация о приложении
        </div>
        <div class="endpoint">
            <code>POST /api/message</code> - Отправить сообщение (JSON body: {"message": "text"})
        </div>
        <div class="endpoint">
            <code>GET /metrics</code> - Prometheus метрики
        </div>
        
        <div class="notes-section">
            <h3>📝 Управление заметками (Notes API):</h3>
            <div class="endpoint">
                <code>POST /api/notes</code> - Создать новую заметку (rate limited to 20/min)
            </div>
            <div class="endpoint">
                <code>GET /api/notes</code> - Получить все заметки (с пагинацией: skip, limit)
            </div>
            <div class="endpoint">
                <code>GET /api/notes/<id></code> - Получить заметку по ID
            </div>
            <div class="endpoint">
                <code>PUT /api/notes/<id></code> - Обновить заметку (rate limited to 30/min)
            </div>
            <div class="endpoint">
                <code>DELETE /api/notes/<id></code> - Удалить заметку (rate limited to 10/min)
            </div>
            <div class="endpoint">
                <code>GET /api/notes/search?q=<query></code> - Поиск заметок по заголовку или содержимому
            </div>
        </div>
    </div>
</body>
</html>
"""


def home_controller():
    """Контроллер для главной страницы"""
    return render_template_string(
        HTML_TEMPLATE,
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
        hostname=config.HOSTNAME,
        timestamp=datetime.now().isoformat()
    )


def health_check_controller():
    """Контроллер для health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': config.APP_VERSION
    }), 200


def get_info_controller():
    """Контроллер для получения информации о приложении"""
    # Попробуем получить данные из кэша
    cache_key = f"app_info_{config.HOSTNAME}_{config.APP_VERSION}"
    cached_response = cache_manager.get(cache_key)
    
    if cached_response:
        logger.debug("Retrieved info from cache", cache_key=cache_key)
        return cached_response, 200
    
    # Если в кэше нет, формируем ответ
    response_data = {
        'name': 'K3s CI/CD Demo',
        'version': config.APP_VERSION,
        'environment': config.ENVIRONMENT,
        'pod_name': config.HOSTNAME,
        'timestamp': datetime.now().isoformat()
    }
    
    response = jsonify(response_data)
    
    # Сохраняем в кэш на 5 минут (если кэш доступен)
    # Не логируем ошибку, так как cache_manager уже обрабатывает ошибки
    cache_manager.set(cache_key, response, timeout=300)
    
    return response, 200


def receive_message_controller():
    """Контроллер для получения сообщений"""
    try:
        # Проверяем, является ли запрос JSON
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        # Используем схему валидации
        message_schema = MessageSchema()
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Failed to decode JSON object'}), 400

        if data is None:
            return jsonify({'error': 'Failed to decode JSON object'}), 400

        # Валидируем данные
        try:
            result = message_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        # Обрабатываем сообщение
        message = result['message']
        response = message_service.process_message(message, config.HOSTNAME)
        return jsonify(response), 201

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def metrics_controller():
    """Контроллер для метрик (Prometheus format)"""
    global request_count
    uptime = time.time() - start_time
    return f"""# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="{config.APP_VERSION}",environment="{config.ENVIRONMENT}",pod="{config.HOSTNAME}"}} 1

# HELP app_requests_total Total requests processed
# TYPE app_requests_total counter
app_requests_total {request_count}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime}

# HELP app_current_datetime Current datetime
# TYPE app_current_datetime gauge
app_current_datetime{{timestamp="{datetime.now().isoformat()}"}} 1
""", 200, {'Content-Type': 'text/plain; charset=utf-8'}


def ping_controller():
    """Контроллер для ping endpoint"""
    return jsonify({'pong': True, 'timestamp': datetime.now().isoformat()}), 200


def not_found_controller(error):
    """Контроллер для 404 ошибки"""
    return jsonify({'error': 'Endpoint not found'}), 404


def internal_error_controller(error):
    """Контроллер для 500 ошибки"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


def before_request_handler():
    """Обработчик перед запросом для подсчета метрик"""
    global request_count
    request_count += 1