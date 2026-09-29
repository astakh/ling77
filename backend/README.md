# WordFlow Backend

FastAPI backend для платформы интервального повторения английских слов.

## Стек

- **Python 3.11+** + **FastAPI** (async)
- **SQLAlchemy 2.0** (async) + **Alembic** для миграций
- **PostgreSQL 14+**
- **GigaChat API** для генерации упражнений и оценки переводов
- **JWT** (access + refresh tokens с ротацией)

## Установка

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `.env.example` в `.env` и заполните:
```bash
cp .env.example .env
```

2. Создайте базу данных PostgreSQL:
```sql
CREATE DATABASE wordflow;
```

3. Запустите миграции:
```bash
alembic upgrade head
```

## Запуск

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API документация: http://localhost:8000/docs

## API Endpoints

### Auth
- `POST /auth/register` — регистрация
- `POST /auth/login` — вход
- `POST /auth/refresh` — обновление токена
- `POST /auth/logout` — выход

### Onboarding
- `POST /onboarding/complete` — завершение онбординга

### Dashboard
- `GET /dashboard/summary` — сводка (CTA, стрик, статистика)

### Lesson
- `POST /lesson/preview` — превью состава урока
- `POST /lesson/new-word/decline` — исключить слово
- `POST /lesson/start` — начать урок (LLM генерация)
- `POST /lesson/evaluate` — оценить перевод (LLM)
- `GET /lesson/{id}/summary` — итоги урока
- `POST /lesson/{id}/abandon` — прервать урок

### Vocabulary
- `GET /vocabulary/list` — список слов (пагинация, фильтры)
- `PATCH /vocabulary/word/{id}/status` — сменить статус

### Admin
- `POST /admin/dictionaries/import` — импорт словаря
- `GET /admin/reports/summary` — отчёт

## Архитектура

### SRS (Интервальное повторение)
- 7 стадий (0-6), интервалы в уроках: [1, 2, 3, 7, 11, 30]
- Успех: stage + 1, Ошибка: max(stage - 1, 0)
- При stage = 6 → mastered, due = NULL

### Безопасность
- Пароли: bcrypt
- JWT: короткий TTL (15 мин)
- Refresh tokens: хеш в БД, ротация, family_id
- Rate limiting: 10 req/min на auth endpoints
- CORS: строго по доменам

### LLM (GigaChat)
- Токен: single-flight refresh в памяти
- Таймауты: 45с (генерация), 15с (оценка)
- Retry: 401 → refresh + retry, 429 → backoff, 5xx → 2 retries
- Защита от инъекций: user input в `<<<UT_{random}>>>`
- Все вызовы логируются в `llm_calls`

### Идемпотентность
- `Idempotency-Key` header для /lesson/start и /lesson/evaluate
- Advisory locks на профиль при старте урока
- `SELECT ... FOR UPDATE` для критических транзакций

## Структура проекта

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Settings (pydantic-settings)
├── database.py          # Async SQLAlchemy setup
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── auth.py              # JWT + password hashing
├── srs.py               # SRS algorithm
├── llm_client.py        # GigaChat client
├── routes/
│   ├── auth.py          # Auth endpoints
│   ├── onboarding.py    # Onboarding
│   ├── dashboard.py     # Dashboard summary
│   ├── lesson.py        # Lesson flow (start, evaluate, summary)
│   ├── vocabulary.py    # Vocabulary management
│   └── admin.py         # Admin endpoints
├── alembic/             # Database migrations
├── requirements.txt
└── .env.example
```

## Разработка

### Создание миграции
```bash
alembic revision --autogenerate -m "description"
```

### Применение миграций
```bash
alembic upgrade head
```

### Откат миграции
```bash
alembic downgrade -1
```

## Лицензия

MIT
