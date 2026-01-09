#!/usr/bin/env python3
"""
Simple Flask application for K3s deployment demo
"""
import os
import logging
import re
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS
CORS(app)

# Security headers
@app.after_request
def after_request(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response

# Configuration
VERSION = os.getenv('APP_VERSION', '1.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
HOSTNAME = os.getenv('HOSTNAME', 'unknown')
MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '1000'))

# Input validation helper
def validate_input(data, field_name, max_length=None, pattern=None):
    """Validate input field"""
    if not data or field_name not in data:
        return False, f"{field_name} field is required"
    
    value = data[field_name]
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"
    
    if max_length and len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length}"
    
    if pattern and not re.match(pattern, value):
        return False, f"{field_name} does not match required pattern"
    
    return True, value

# Simple HTML template for main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>K3s Demo App</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .info { background-color: #e8f4f8; padding: 15px; border-left: 4px solid #00bcd4; margin: 20px 0; }
        code { background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        .endpoint { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 4px; }
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
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def home():
    """Main page"""
    return render_template_string(
        HTML_TEMPLATE,
        version=VERSION,
        environment=ENVIRONMENT,
        hostname=HOSTNAME,
        timestamp=datetime.now().isoformat()
    )


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for K8s liveness/readiness probes"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION
    }), 200


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get application information"""
    return jsonify({
        'name': 'K3s CI/CD Demo',
        'version': VERSION,
        'environment': ENVIRONMENT,
        'pod_name': HOSTNAME,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/message', methods=['POST'])
def receive_message():
    """Receive and process a message"""
    try:
        # Check if request contains JSON
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        
        # Validate input
        is_valid, result = validate_input(data, 'message', max_length=MAX_MESSAGE_LENGTH)
        if not is_valid:
            return jsonify({'error': result}), 400
        
        message = result
        # Additional sanitization if needed
        sanitized_message = message.strip()
        
        logger.info(f"Received message: {sanitized_message}")
        
        return jsonify({
            'success': True,
            'message': f'Сообщение получено: {sanitized_message}',
            'processed_at': datetime.now().isoformat(),
            'pod': HOSTNAME
        }), 201
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/metrics', methods=['GET'])
def metrics():
    """Simple metrics endpoint (Prometheus format)"""
    return f"""# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="{VERSION}",environment="{ENVIRONMENT}",pod="{HOSTNAME}"}} 1

# HELP app_requests_total Total requests processed
# TYPE app_requests_total counter
app_requests_total 0

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds 0
""", 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/api/ping', methods=['GET'])
def ping():
    """Simple ping endpoint"""
    return jsonify({'pong': True, 'timestamp': datetime.now().isoformat()}), 200


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# Apply ProxyFix to handle headers from reverse proxy (Traefik)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = ENVIRONMENT == 'development'
    logger.info(f"Starting application on port {port}")
    logger.info(f"Version: {VERSION}, Environment: {ENVIRONMENT}")
    app.run(host='0.0.0.0', port=port, debug=debug)
