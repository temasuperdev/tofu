# Архитектура микросервисного приложения заметок

## Общая архитектура

```mermaid
graph TB
    subgraph "Клиент"
        A[Browser] --> B[Vue.js Frontend]
    end
    
    subgraph "Kubernetes Cluster"
        B --> C[FastAPI Backend]
        C --> D[PostgreSQL DB]
        
        E[Traefik Ingress] --> B
        E --> C
        
        F[k3s Nodes] --> E
        F --> G[Persistent Volumes]
    end
    
    subgraph "CI/CD"
        H[GitHub Actions] --> I[Docker Registry]
        I --> J[Kubernetes Deployments]
    end
```

## Взаимодействие между сервисами

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (Vue.js)
    participant B as Backend (FastAPI)
    participant D as Database (PostgreSQL)
    
    U->>+F: Открыть приложение
    F->>+B: GET /api/notes
    B->>+D: SELECT * FROM notes
    D-->>-B: Данные заметок
    B-->>-F: JSON данные
    F-->>-U: Отображение заметок
    
    U->>+F: Создать заметку
    F->>+B: POST /api/notes
    B->>+D: INSERT INTO notes
    D-->>-B: Заметка сохранена
    B-->>-F: Ответ об успехе
    F-->>-U: Заметка создана
```

## Безопасность и доступ

- DNS: serv.temasuug.ru
- HTTPS: Обеспечен через Traefik + Let's Encrypt
- Аутентификация: JWT токены
- Сетевая изоляция: NetworkPolicies