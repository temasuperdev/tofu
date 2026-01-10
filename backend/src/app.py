#!/usr/bin/env python3
"""
Simple Flask application for K3s deployment demo
"""
import os
import logging
import time
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
from .config import get_config
from .controllers.api_controllers import (
    home_controller,
    health_check_controller,
    get_info_controller,
    receive_message_controller,
    metrics_controller,
    ping_controller,
    not_found_controller,
    internal_error_controller,
    before_request_handler
)
from .utils.cache_manager import cache_manager
from .utils.swagger_config import configure_swagger

# Get configuration
config = get_config()

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
app.config.from_object(config)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Attach limiter to app
limiter.init_app(app)

# Initialize cache
cache_manager.init_app(app)

# Initialize Swagger
swagger = configure_swagger(app)

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

# Configuration from config object
VERSION = config.APP_VERSION
ENVIRONMENT = config.ENVIRONMENT
HOSTNAME = config.HOSTNAME

# Routes
@app.route('/', methods=['GET'])
def home():
    """Main page"""
    return home_controller()


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Health
    responses:
      200:
        description: Application is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            timestamp:
              type: string
              example: "2023-01-01T12:00:00Z"
            version:
              type: string
              example: "1.0.0"
    """
    return health_check_controller()


@app.route('/api/info', methods=['GET'])
def get_info():
    """
    Get application information
    ---
    tags:
      - Info
    responses:
      200:
        description: Application information
        schema:
          type: object
          properties:
            name:
              type: string
              example: "K3s CI/CD Demo"
            version:
              type: string
              example: "1.0.0"
            environment:
              type: string
              example: "development"
            pod_name:
              type: string
              example: "demo-app-12345"
            timestamp:
              type: string
              example: "2023-01-01T12:00:00Z"
    """
    return get_info_controller()


@app.route('/api/message', methods=['POST'])
@limiter.limit("10 per minute")
def receive_message():
    """
    Receive and process a message
    ---
    tags:
      - Messages
    parameters:
      - in: body
        name: message
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              example: "This is a test message"
              maxLength: 1000
    responses:
      201:
        description: Message received successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Сообщение получено: This is a test message"
            processed_at:
              type: string
              example: "2023-01-01T12:00:00Z"
            pod:
              type: string
              example: "demo-app-12345"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Message field is required"
    """
    return receive_message_controller()


@app.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus metrics endpoint
    ---
    tags:
      - Metrics
    responses:
      200:
        description: Prometheus metrics
        content:
          text/plain:
            schema:
              type: string
    """
    return metrics_controller()


@app.route('/api/ping', methods=['GET'])
def ping():
    """
    Ping endpoint
    ---
    tags:
      - Health
    responses:
      200:
        description: Ping response
        schema:
          type: object
          properties:
            pong:
              type: boolean
              example: true
            timestamp:
              type: string
              example: "2023-01-01T12:00:00Z"
    """
    return ping_controller()


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return not_found_controller(error)


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return internal_error_controller(error)


@app.before_request
def before_request():
    """Before request handler"""
    before_request_handler()


# Apply ProxyFix to handle headers from reverse proxy (Traefik)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

if __name__ == '__main__':
    port = config.PORT
    debug = config.ENVIRONMENT == 'development'
    logger.info(f"Starting application on port {port}")
    logger.info(f"Version: {VERSION}, Environment: {ENVIRONMENT}")
    app.run(host='0.0.0.0', port=port, debug=debug)