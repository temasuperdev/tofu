# API Documentation

This document describes the API endpoints of the K3s Demo Application.

## Base URL

All API endpoints are relative to the base URL where the application is deployed.

## Authentication

No authentication is required for any of the endpoints described below.

## Endpoints

### GET /

Returns the main HTML page with application information and API documentation.

**Response:**
- Status: 20 OK
- Content-Type: text/html

### GET /api/health

Health check endpoint for K8s liveness/readiness probes.

**Response:**
- Status: 200 OK
- Content-Type: application/json

```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:34:56.789123",
  "version": "1.0.0"
}
```

### GET /api/info

Get application information.

**Response:**
- Status: 200 OK
- Content-Type: application/json

```json
{
  "name": "K3s CI/CD Demo",
  "version": "1.0.0",
  "environment": "development",
  "pod_name": "unknown",
  "timestamp": "2023-10-01T12:34:56.789123"
}
```

### POST /api/message

Receive and process a message.

**Request:**
- Content-Type: application/json
- Body:
```json
{
  "message": "string (max 1000 characters)"
}
```

**Response:**
- Status: 201 Created
- Content-Type: application/json

```json
{
 "success": true,
  "message": "Сообщение получено: [your message]",
  "processed_at": "2023-10-01T12:34:56.789123",
  "pod": "unknown"
}
```

**Errors:**
- Status: 400 Bad Request - if message field is missing, not a string, or exceeds max length
- Status: 500 Internal Server Error - if an internal error occurs

### GET /metrics

Prometheus metrics endpoint.

**Response:**
- Status: 200 OK
- Content-Type: text/plain; charset=utf-8

```
# HELP app_info Application information
# TYPE app_info gauge
app_info{version="1.0.0",environment="development",pod="unknown"} 1

# HELP app_requests_total Total requests processed
# TYPE app_requests_total counter
app_requests_total 10

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds 1234.567

# HELP app_current_datetime Current datetime
# TYPE app_current_datetime gauge
app_current_datetime{timestamp="2023-10-01T12:34:56.789123"} 1
```

### GET /api/ping

Simple ping endpoint.

**Response:**
- Status: 200 OK
- Content-Type: application/json

```json
{
  "pong": true,
  "timestamp": "2023-10-01T12:34:56.789123"
}
```

## Error Responses

When an error occurs, the API returns a JSON object with an error message:

```json
{
  "error": "Description of the error"
}
```

## Configuration

The application behavior can be configured using environment variables:

- `APP_VERSION`: Version of the application (default: "1.0.0")
- `ENVIRONMENT`: Environment name (default: "development")
- `HOSTNAME`: Hostname identification (default: "unknown")
- `MAX_MESSAGE_LENGTH`: Maximum length of messages (default: 1000)
- `PORT`: Port number to listen on (default: 5000)
- `LOG_LEVEL`: Logging level (default: "INFO")

## Security Headers

The application sets the following security headers on all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains`