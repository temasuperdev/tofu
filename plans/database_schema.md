# Схема базы данных для приложения заметок

## 1. Описание сущностей

### 1.1. Таблица пользователей (users)
Хранит информацию о зарегистрированных пользователях.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

Индексы:
- `idx_users_username`: INDEX ON users(username)
- `idx_users_email`: INDEX ON users(email)
- `idx_users_created_at`: INDEX ON users(created_at)

### 1.2. Таблица заметок (notes)
Хранит заметки пользователей с возможностью установки видимости.

```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

Индексы:
- `idx_notes_user_id`: INDEX ON notes(user_id)
- `idx_notes_is_public`: INDEX ON notes(is_public)
- `idx_notes_created_at`: INDEX ON notes(created_at)
- `idx_notes_tags`: GIN INDEX ON notes USING GIN(tags)

### 1.3. Таблица сессий (sessions)
Хранит активные сессии пользователей (опционально, если не используем JWT).

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

Индексы:
- `idx_sessions_token`: INDEX ON sessions(token)
- `idx_sessions_user_id`: INDEX ON sessions(user_id)
- `idx_sessions_expires_at`: INDEX ON sessions(expires_at)

## 2. Триггеры и функции

### 2.1. Функция обновления поля updated_at
Обновляет поле `updated_at` при изменении записи.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применение к таблицам
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 3. Представления

### 3.1. Представление публичных заметок
```sql
CREATE VIEW public_notes AS
SELECT n.id, n.title, n.content, n.user_id, u.username, n.created_at, n.updated_at
FROM notes n
JOIN users u ON n.user_id = u.id
WHERE n.is_public = TRUE;
```

## 4. Примеры запросов

### 4.1. Получить все заметки пользователя
```sql
SELECT id, title, content, is_public, created_at, updated_at
FROM notes
WHERE user_id = $1
ORDER BY created_at DESC;
```

### 4.2. Поиск заметок по тегам
```sql
SELECT id, title, content, user_id, created_at
FROM notes
WHERE tags ? $1  -- Проверяет наличие тега в JSONB массиве
AND user_id = $2;
```

### 4.3. Создать новую заметку
```sql
INSERT INTO notes (title, content, user_id, is_public, tags)
VALUES ($1, $2, $3, $4, $5)
RETURNING id, created_at, updated_at;
```

## 5. Миграции с использованием Alembic

### 5.1. Структура файлов миграций
```
alembic/
├── versions/
│   ├── 001_initial_migration.py
│   ├── 002_add_tags_to_notes.py
│   └── ...
├── env.py
├── script.py.mako
└── alembic.ini
```

### 5.2. Пример миграции
```python
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('tags', sa.JSON(), server_default='[]', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_created_at'), 'notes', ['created_at'], unique=False)
    op.create_index(op.f('ix_notes_is_public'), 'notes', ['is_public'], unique=False)
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_is_public'), table_name='notes')
    op.drop_index(op.f('ix_notes_created_at'), table_name='notes')
    op.drop_table('notes')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
```

## 6. Настройка репликации

Для обеспечения отказоустойчивости рекомендуется настроить потоковую репликацию PostgreSQL:

- Master сервер: основной источник данных
- Standby серверы: реплики для отказоустойчивости и балансировки чтения

## 7. Резервное копирование

Регулярные процедуры резервного копирования:
- Ежедневный pg_dump для полного бэкапа
- WAL архивирование для Point-in-Time Recovery
- Хранение бэкапов в S3-совместимом хранилище