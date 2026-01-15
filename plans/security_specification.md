# Спецификация безопасности для микросервисного приложения заметок

## 1. Обзор безопасности

Приложение реализует многоуровневую модель безопасности, включающую:
- Аутентификацию и авторизацию пользователей
- Защиту от распространенных веб-угроз
- Безопасную передачу данных
- Защиту инфраструктуры

## 2. Аутентификация и авторизация

### 2.1. Модель аутентификации
- Использование JWT токенов для аутентификации
- Временные токены доступа (access tokens) с коротким сроком действия (30 минут)
- Долгосрочные токены обновления (refresh tokens) с длительным сроком действия (7 дней)
- Хэширование паролей с использованием bcrypt

### 2.2. Реализация в FastAPI
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Настройка контекста хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user
```

### 2.3. Защита эндпоинтов
Все эндпоинты управления заметками требуют аутентификации:
```python
@router.get("/notes/{note_id}")
async def read_note(note_id: int, current_user: User = Depends(get_current_user)):
    # Проверка принадлежности заметки пользователю
    note = get_note_by_id(note_id)
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return note
```

## 3. Защита от веб-угроз

### 3.1. Защита от XSS (Cross-Site Scripting)
- Санитизация выводимых данных
- Использование контекстного экранирования
- Установка заголовков безопасности:

```python
from starlette.middleware import Middleware
from starlette.middleware.security import SecurityMiddleware

middleware = [
    Middleware(SecurityMiddleware, 
               content_type_nosniff=True,
               xss_protection=True)
]
```

### 3.2. Защита от CSRF (Cross-Site Request Forgery)
- Использование stateful сессий с CSRF токенами для чувствительных операций
- Проверка происхождения запросов (Origin, Referer headers)

### 3.3. Защита от SQL-инъекций
- Использование ORM (SQLAlchemy) вместо сырых SQL запросов
- Валидация и параметризация всех входных данных

### 3.4. Валидация входных данных
Использование Pydantic моделей для валидации:
```python
class NoteCreate(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=10000)
    is_public: bool = False
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

## 4. Безопасная передача данных

### 4.1. HTTPS
- Все соединения шифруются с использованием TLS 1.2+
- Принудительная переадресация HTTP → HTTPS
- HSTS заголовки для предотвращения downgrade атак

### 4.2. CORS политика
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://serv.temasuug.ru"],  # Только доверенные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400  # 24 часа
)
```

## 5. Безопасность инфраструктуры

### 5.1. Безопасность в Kubernetes

#### 5.1.1. Pod Security Standards
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: notes-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### 5.1.2. SecurityContext для подов
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: backend
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
```

### 5.2. Network Policies
Ограничение сетевого трафика между подами:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-netpol
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

## 6. Управление секретами

### 6.1. Kubernetes Secrets
- Хранение чувствительных данных в encrypted secrets
- Использование внешних решений для управления секретами (HashiCorp Vault, AWS Secrets Manager)

### 6.2. Пример безопасного использования секретов
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
data:
  db-password: <base64-encoded-password>
  jwt-secret: <base64-encoded-jwt-secret>
```

```python
# В приложении
import os

DB_PASSWORD = os.getenv("DB_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")
```

## 7. Логирование и аудит

### 7.1. Безопасное логирование
- Не логировать чувствительные данные (пароли, токены)
- Использование структурированных логов
- Логирование попыток несанкционированного доступа

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None):
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "ip_address": ip_address
    }
    logger.warning(json.dumps(log_data))
```

## 8. Безопасность базы данных

### 8.1. PostgreSQL
- Использование ролей с минимальными необходимыми правами
- SSL соединения с базой данных
- Регулярные обновления версии PostgreSQL

### 8.2. Защита данных
- Шифрование чувствительных данных на уровне приложения при необходимости
- Регулярные бэкапы с шифрованием

## 9. Пентестинг и безопасность CI/CD

### 9.1. Сканирование уязвимостей
- Сканирование образов контейнеров на наличие CVE
- Проверка зависимостей на уязвимости
- Статический анализ безопасности кода

### 9.2. Пример GitHub Actions для сканирования
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/${{ github.repository }}/backend:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy scan results to GitHub Security tab
  uses: github/codeql-action/upload-sarif@v2
  if: always()
  with:
    sarif_file: 'trivy-results.sarif'
```

## 10. Рекомендации по безопасности

### 10.1. Регулярные обновления
- Поддержание актуальных версий зависимостей
- Обновление базовых образов контейнеров
- Регулярные обновления Kubernetes

### 10.2. Мониторинг безопасности
- Мониторинг аномального поведения
- Оповещения о подозрительной активности
- Регулярные аудиты безопасности