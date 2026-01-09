# План реорганизации структуры проекта

## Цель
Создать структурированную систему папок для улучшения организации проекта, ориентированную на микросервисы с отдельными папками для каждого компонента (backend, k8s, docker).

## Предлагаемая структура папок
```
tofu/
├── backend/                    # Основное приложение
│   ├── src/                   # Исходный код Python
│   │   ├── __init__.py
│   │   └── app.py
│   ├── tests/                 # Тесты
│   │   ├── __init__.py
│   │   └── test_app.py
│   ├── requirements.txt       # Зависимости Python
│   └── setup.py              # Файл установки
├── k8s/                      # Kubernetes конфигурации
│   ├── deployment.yaml       # Deployment и связанные ресурсы
│   ├── deployment-production.yaml
│   ├── deployment-simple.yaml
│   ├── deployment-working.yaml
│   ├── ingress.yaml          # Ingress и сетевые настройки
│   ├── ingressroute.yaml
│   ├── letsencrypt-issuer.yaml
│   ├── networkpolicy.yaml
│   └── namespace.yaml        # Определение namespace
├── docker/                   # Docker конфигурации
│   ├── Dockerfile           # Основной Dockerfile
│   ├── docker-compose.yaml  # Docker Compose конфигурация
│   └── .dockerignore        # Файлы игнорирования для Docker
├── scripts/                  # Скрипты автоматизации
│   ├── build.sh             # Скрипт сборки
│   ├── build-local.sh
│   ├── cleanup-local.sh
│   ├── deploy.sh            # Скрипт деплоя
│   ├── deploy-local.sh
│   ├── deploy-local-k3s.sh
│   ├── make-local.sh
│   ├── registry.sh
│   ├── setup-local.sh
│   ├── show-local-setup.sh
│   └── test-app-locally.sh
├── docs/                     # Документация
│   ├── README.md            # Главный файл документации
│   ├── README_MAIN.md
│   ├── CI_CD_GUIDE.md
│   ├── CI_CD_HEALTH_CHECK_FIX.md
│   ├── CI_CD_HEALTH_CHECK_RESOLVED.md
│   ├── DNS_HTTPS_SETUP.md
│   ├── DOCUMENTATION_MAP.md
│   ├── GITHUB_ACTIONS_FIX.md
│   ├── K3S_DEPLOYMENT.md
│   ├── LOCAL_QUICKSTART.md
│   ├── LOCAL_SETUP_SUMMARY.md
│   ├── LOCAL_SETUP.md
│   ├── PROJECT_SUMMARY.md
│   ├── QUICKSTART.md
│   ├── SOLUTION_SUMMARY.md
│   ├── TROUBLESHOOTING_404.md
│   ├── TROUBLESHOOTING.md
│   └── .gitignore           # Git ignore для документации
├── configs/                  # Конфигурационные файлы
│   ├── .env.example         # Пример переменных окружения
│   └── .env.local          # Локальные переменные окружения
├── Makefile                 # Make команды
├── LICENSE                  # Лицензия
└── .gitignore              # Основной git ignore
```

## Преимущества новой структуры
1. **Логическая группировка**: Все компоненты связанной функциональности находятся в одной папке
2. **Легкость навигации**: Простое нахождение нужных файлов по их назначению
3. **Поддержка микросервисов**: Возможность легко добавлять новые сервисы в будущем
4. **Четкое разделение ответственности**: Отдельные папки для кода, инфраструктуры и документации

## Замечания по реализации
- Некоторые файлы, такие как `.gitignore`, могут потребовать обновления путей
- Файлы в `k8s/` могут ссылаться на пути, которые изменятся при перемещении
- Makefile может потребовать обновления путей к файлам
- Dockerfile может потребовать обновления путей к исходному коду