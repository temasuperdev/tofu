import pytest
from src.app import app
from src.config import TestingConfig
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a test client"""
    app.config.from_object(TestingConfig())
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'K3s CI/CD Demo' in response.data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


def test_info_endpoint(client):
    """Test info endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    assert 'version' in response.json
    assert 'name' in response.json


def test_ping_endpoint(client):
    """Test ping endpoint"""
    response = client.get('/api/ping')
    assert response.status_code == 200
    assert response.json['pong'] is True


def test_message_endpoint_success(client):
    """Test message endpoint with valid data"""
    response = client.post('/api/message',
                          json={'message': 'Test message'},
                          content_type='application/json')
    assert response.status_code == 201
    assert response.json['success'] is True


def test_message_endpoint_missing_data(client):
    """Test message endpoint with missing data"""
    response = client.post('/api/message',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json


def test_message_endpoint_invalid_json(client):
    """Test message endpoint with invalid JSON"""
    response = client.post('/api/message',
                          data='invalid json',
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json


def test_message_endpoint_too_long(client):
    """Test message endpoint with too long message"""
    long_message = 'A' * 1001  # Exceeds default max length of 1000
    response = client.post('/api/message',
                          json={'message': long_message},
                          content_type='application/json')
    assert response.status_code == 400
    assert 'error' in response.json


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'app_info' in response.data
    assert b'app_requests_total' in response.data
    assert b'app_uptime_seconds' in response.data


def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404


def test_cache_manager_has_method(client):
    """Test cache manager has method"""
    from src.utils.cache_manager import cache_manager
    # Проверяем, что метод has() существует
    assert hasattr(cache_manager, 'has')
    # Проверяем, что метод возвращает False для несуществующего ключа
    assert cache_manager.has('nonexistent_key') is False