import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
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
    response = client.post('/api/message', json={'message': 'Test message'})
    assert response.status_code == 201
    assert response.json['success'] is True


def test_message_endpoint_missing_data(client):
    """Test message endpoint with missing data"""
    response = client.post('/api/message', json={})
    assert response.status_code == 400
    assert 'error' in response.json


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'app_info' in response.data


def test_404_error(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
