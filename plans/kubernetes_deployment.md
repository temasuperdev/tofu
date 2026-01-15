# Kubernetes Deployment для микросервисного приложения заметок

## 1. Общая архитектура в Kubernetes

```
k3s Cluster
├── Namespace: notes-app
│   ├── PostgreSQL Deployment
│   ├── PostgreSQL Service
│   ├── PostgreSQL PersistentVolumeClaim
│   ├── Backend Deployment
│   ├── Backend Service
│   ├── Frontend Deployment
│   ├── Frontend Service
│   └── Ingress (Traefik)
```

## 2. Namespace и конфигурация

### 2.1. Namespace (k8s/namespace.yaml)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: notes-app
```

### 2.2. ConfigMap для настроек (k8s/backend/configmap.yaml)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: notes-app
data:
  DATABASE_URL: "postgresql://postgres:password@postgres-service:5432/notesdb"
  SECRET_KEY: "your-secret-key-here"
  ALGORITHM: "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: "30"
  REFRESH_TOKEN_EXPIRE_DAYS: "7"
```

## 3. PostgreSQL Deployment

### 3.1. Secret для учетных данных (k8s/postgres/secret.yaml)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: notes-app
type: Opaque
data:
  postgres-password: cG9zdGdyZXMK (base64 encoded "postgres")
  postgres-db: bm90ZXNkYgo= (base64 encoded "notesdb")
```

### 3.2. PersistentVolumeClaim (k8s/postgres/pvc.yaml)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: notes-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: local-path  # Используется стандартный storage class в k3s
```

### 3.3. Deployment (k8s/postgres/deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
  namespace: notes-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: postgres-db
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: postgres-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -h
            - localhost
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -h
            - localhost
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: notes-app
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

## 4. Backend Deployment

### 4.1. Deployment (k8s/backend/deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: notes-app
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/username/notes-app/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: backend-config
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgres-service:5432/$(POSTGRES_DB)"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: notes-app
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

## 5. Frontend Deployment

### 5.1. Deployment (k8s/frontend/deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: notes-app
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ghcr.io/username/notes-app/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: notes-app
spec:
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

## 6. Ingress и SSL

### 6.1. Ingress с TLS (k8s/ingress.yaml)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: notes-app-ingress
  namespace: notes-app
  annotations:
    kubernetes.io/ingress.class: "traefik"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"  # Если используется cert-manager
    traefik.ingress.kubernetes.io/router.entrypoints: "websecure"
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  tls:
  - hosts:
    - serv.temasuug.ru
    secretName: serv-tls-certificate
  rules:
  - host: serv.temasuug.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

## 7. Network Policies

### 7.1. Защита трафика между сервисами (k8s/network-policy.yaml)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: notes-app
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
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
  namespace: notes-app
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8000
```

## 8. Horizontal Pod Autoscaler

### 8.1. Автоматическое масштабирование (k8s/hpa.yaml)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: notes-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: notes-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-deployment
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 9. Monitoring и Logging

### 9.1. ServiceMonitor для Prometheus (если установлен)
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
  namespace: notes-app
  labels:
    app: backend
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics  # Должен быть открыт порт метрик в приложении
    interval: 30s
```

## 10. Deployment команды

### 10.1. Применение манифестов
```bash
# Создание namespace
kubectl apply -f k8s/namespace.yaml

# PostgreSQL
kubectl apply -f k8s/postgres/ -n notes-app

# Ждем готовности PostgreSQL
kubectl wait --for=condition=ready pod -l app=postgres -n notes-app --timeout=300s

# Backend
kubectl apply -f k8s/backend/ -n notes-app

# Frontend
kubectl apply -f k8s/frontend/ -n notes-app

# Ingress
kubectl apply -f k8s/ingress.yaml -n notes-app
```

## 11. Безопасность в Kubernetes

### 11.1. SecurityContext
- Запуск контейнеров от non-root пользователя
- ReadOnlyRootFilesystem для контейнеров где возможно
- Privileged контейнеры запрещены
- Seccomp и AppArmor профили

### 11.2. RBAC
- Минимальные необходимые права для сервисных аккаунтов
- Network policies для ограничения трафика
- ImagePullSecrets для приватных репозиториев