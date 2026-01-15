# Notes Application

A microservices-based note-taking application built with FastAPI, Vue.js, and PostgreSQL, deployed on Kubernetes.

## Architecture Overview

The application follows a microservices architecture consisting of:

- **Frontend**: Vue.js single-page application
- **Backend**: FastAPI REST API
- **Database**: PostgreSQL
- **Infrastructure**: Kubernetes cluster with Traefik ingress controller

## Features

- User authentication and authorization with JWT
- CRUD operations for notes
- Public/private note visibility
- Responsive web interface
- Kubernetes-native deployment
- CI/CD pipeline with GitHub Actions

## Tech Stack

### Backend (FastAPI)
- Python 3.9+
- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication
- Alembic for migrations

### Frontend (Vue.js)
- Vue.js 3
- Pinia for state management
- Vue Router
- Tailwind CSS
- Axios for API calls

### Infrastructure
- Docker
- Kubernetes (k3s)
- PostgreSQL
- Traefik ingress controller
- GitHub Actions for CI/CD

## Getting Started

### Prerequisites
- Docker
- Kubernetes cluster (or minikube/kind for local development)
- kubectl

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run serve
```

### Deployment

The application is designed to be deployed on Kubernetes. Apply the manifests in the following order:

1. `kubectl apply -f k8s/namespace.yaml`
2. `kubectl apply -f k8s/postgres/`
3. `kubectl apply -f k8s/backend/`
4. `kubectl apply -f k8s/frontend/`
5. `kubectl apply -f k8s/ingress.yaml`

## API Endpoints

### Authentication
- `POST /api/v1/register` - Register a new user
- `POST /api/v1/login` - Login and get JWT token

### Notes
- `GET /api/v1/notes` - Get all user's notes
- `POST /api/v1/notes` - Create a new note
- `GET /api/v1/notes/{id}` - Get a specific note
- `PUT /api/v1/notes/{id}` - Update a note
- `DELETE /api/v1/notes/{id}` - Delete a note

## Security

- JWT-based authentication
- Passwords are hashed with bcrypt
- Input validation with Pydantic
- Protection against common web vulnerabilities (XSS, CSRF)
- Network policies in Kubernetes

## CI/CD Pipeline

The application includes a complete CI/CD pipeline using GitHub Actions:
- Automated testing for both frontend and backend
- Docker image building and publishing
- Staging and production deployments
- Health checks and notifications

## Environment Variables

### Backend
- `POSTGRES_SERVER` - PostgreSQL server address
- `POSTGRES_USER` - PostgreSQL user
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - PostgreSQL database name
- `SECRET_KEY` - JWT secret key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License