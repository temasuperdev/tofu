# API Documentation

This document describes the API endpoints available in the application.

## Endpoints

### Health Check
- `GET /api/health` - Returns application health status

### Application Info
- `GET /api/info` - Returns application information

### Message Processing
- `POST /api/message` - Process a message (rate limited to 10 per minute)

### Notes Management (New!)
- `POST /api/notes` - Create a new note (rate limited to 20 per minute)
- `GET /api/notes` - Get all notes (with pagination: skip, limit)
- `GET /api/notes/{id}` - Get a specific note by ID
- `PUT /api/notes/{id}` - Update a specific note (rate limited to 30 per minute)
- `DELETE /api/notes/{id}` - Delete a specific note (rate limited to 10 per minute)
- `GET /api/notes/search?q={query}` - Search notes by title or content (with pagination: skip, limit)

### Metrics
- `GET /metrics` - Prometheus metrics endpoint

### Ping
- `GET /api/ping` - Simple ping endpoint

## Rate Limits

The application implements rate limiting on certain endpoints:

- `/api/message`: 10 requests per minute
- `/api/notes`: 20 requests per minute
- `/api/notes/{id}` (PUT): 30 requests per minute
- `/api/notes/{id}` (DELETE): 10 requests per minute

## Notes Management Details

### Create Note
Creates a new note with the provided title and content.

**Request Body:**
```json
{
  "title": "Note Title",
  "content": "Note content goes here..."
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content goes here...",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Get All Notes
Retrieves all notes with optional pagination.

**Query Parameters:**
- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 100, max: 100): Maximum number of records to return

**Response:**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Note Title",
      "content": "Note content goes here...",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Get Note by ID
Retrieves a specific note by its ID.

**Response:**
```json
{
  "id": 1,
  "title": "Note Title",
  "content": "Note content goes here...",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Update Note
Updates a specific note with the provided fields.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content goes here..."
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated Title",
  "content": "Updated content goes here...",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Delete Note
Deletes a specific note by its ID.

**Response:**
```json
{
  "message": "Note deleted successfully"
}
```

### Search Notes
Searches notes by title or content.

**Query Parameters:**
- `q` (required): Search query string
- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 100, max: 1000): Maximum number of records to return

**Response:**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Note Title",
      "content": "Note content goes here...",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100,
  "query": "search term"
}
```

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Unexpected server error

## Database

The application uses PostgreSQL for storing notes. Connection details can be configured via environment variables:

- `DB_USER` (default: postgres)
- `DB_PASSWORD` (default: postgres)
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: notes_db)
- `DATABASE_URL` (full connection string)