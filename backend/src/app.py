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
from .controllers.note_controllers import (
    create_note_controller,
    get_note_controller,
    get_all_notes_controller,
    update_note_controller,
    delete_note_controller,
    search_notes_controller
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
app.config['CACHE_TYPE'] = config.CACHE_TYPE if hasattr(config, 'CACHE_TYPE') else 'redis'
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

# Wait for database to be ready before starting the application
def wait_for_database(max_retries=30, delay=5):
    """Wait for database to be ready before starting the application"""
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.environ.get('DATABASE_URL', config.SQLALCHEMY_DATABASE_URI if hasattr(config, 'SQLALCHEMY_DATABASE_URI') else None)
    
    if not db_url or 'postgresql' not in db_url:
        logger.info("Using SQLite or no database - skipping database readiness check")
        return True
    
    parsed_url = urlparse(db_url)
    db_host = parsed_url.hostname
    db_port = parsed_url.port or 5432
    db_name = parsed_url.path[1:]  # Remove leading slash
    db_user = parsed_url.username
    db_password = parsed_url.password
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            conn.close()
            logger.info(f"Successfully connected to database at {db_host}:{db_port}")
            return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} to connect to database failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error("Failed to connect to database after all attempts")
                raise e
    return False

# Wait for database before continuing
try:
    wait_for_database()
    logger.info("Database is ready, starting application...")
except Exception as e:
    logger.error(f"Application startup failed due to database connection issue: {e}")
    exit(1)

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


@app.route('/api/notes', methods=['POST'])
@limiter.limit("20 per minute")
def create_note():
    """
    Create a new note
    ---
    tags:
      - Notes
    parameters:
      - in: body
        name: note
        required: true
        schema:
          type: object
          required:
            - title
            - content
          properties:
            title:
              type: string
              example: "My Note Title"
              maxLength: 255
            content:
              type: string
              example: "This is the content of my note..."
    responses:
      201:
        description: Note created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "My Note Title"
            content:
              type: string
              example: "This is the content of my note..."
            created_at:
              type: string
              example: "2023-01-01T12:00:00Z"
            updated_at:
              type: string
              example: "2023-01-01T12:00:00Z"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Title and content are required"
    """
    return create_note_controller()


@app.route('/api/notes', methods=['GET'])
def get_all_notes():
    """
    Get all notes
    ---
    tags:
      - Notes
    parameters:
      - name: skip
        in: query
        type: integer
        required: false
        default: 0
        description: Number of records to skip for pagination
      - name: limit
        in: query
        type: integer
        required: false
        default: 100
        maximum: 1000
        description: Maximum number of records to return
    responses:
      200:
        description: List of notes
        schema:
          type: object
          properties:
            notes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "My Note Title"
                  content:
                    type: string
                    example: "This is the content of my note..."
                  created_at:
                    type: string
                    example: "2023-01-01T12:00:00Z"
                  updated_at:
                    type: string
                    example: "2023-01-01T12:00:00Z"
            total:
              type: integer
              example: 1
            skip:
              type: integer
              example: 0
            limit:
              type: integer
              example: 100
    """
    return get_all_notes_controller()


@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """
    Get a specific note
    ---
    tags:
      - Notes
    parameters:
      - name: note_id
        in: path
        type: integer
        required: true
        description: ID of the note to retrieve
    responses:
      200:
        description: Note details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "My Note Title"
            content:
              type: string
              example: "This is the content of my note..."
            created_at:
              type: string
              example: "2023-01-01T12:00:00Z"
            updated_at:
              type: string
              example: "2023-01-01T12:00:00Z"
      404:
        description: Note not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Note not found"
    """
    return get_note_controller(note_id)


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@limiter.limit("30 per minute")
def update_note(note_id):
    """
    Update a specific note
    ---
    tags:
      - Notes
    parameters:
      - name: note_id
        in: path
        type: integer
        required: true
        description: ID of the note to update
      - in: body
        name: note
        required: false
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Updated Note Title"
              maxLength: 255
            content:
              type: string
              example: "This is the updated content of my note..."
    responses:
      200:
        description: Note updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "Updated Note Title"
            content:
              type: string
              example: "This is the updated content of my note..."
            created_at:
              type: string
              example: "2023-01-01T12:00:00Z"
            updated_at:
              type: string
              example: "2023-01-01T12:00:00Z"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Request must be JSON"
      404:
        description: Note not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Note not found"
    """
    return update_note_controller(note_id)


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_note(note_id):
    """
    Delete a specific note
    ---
    tags:
      - Notes
    parameters:
      - name: note_id
        in: path
        type: integer
        required: true
        description: ID of the note to delete
    responses:
      200:
        description: Note deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Note deleted successfully"
      404:
        description: Note not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Note not found"
    """
    return delete_note_controller(note_id)


@app.route('/api/notes/search', methods=['GET'])
def search_notes():
    """
    Search notes by title or content
    ---
    tags:
      - Notes
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query
      - name: skip
        in: query
        type: integer
        required: false
        default: 0
        description: Number of records to skip for pagination
      - name: limit
        in: query
        type: integer
        required: false
        default: 100
        maximum: 1000
        description: Maximum number of records to return
    responses:
      200:
        description: Search results
        schema:
          type: object
          properties:
            notes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "My Note Title"
                  content:
                    type: string
                    example: "This is the content of my note..."
                  created_at:
                    type: string
                    example: "2023-01-01T12:00:00Z"
                  updated_at:
                    type: string
                    example: "2023-01-01T12:00:00Z"
            total:
              type: integer
              example: 1
            skip:
              type: integer
              example: 0
            limit:
              type: integer
              example: 100
            query:
              type: string
              example: "search term"
      400:
        description: Query parameter is required
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Query parameter \"q\" is required"
    """
    return search_notes_controller()


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