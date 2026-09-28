# WordFlow — Интервальное повторение английских слов

Полноценное веб-приложение для изучения английских слов с помощью интервального повторения и LLM (GigaChat).

## Структура проекта

```
wordflow/
├── src/                    # Frontend (React + Vite + TypeScript + Tailwind)
│   ├── api/               # API клиент для backend
│   ├── pages/             # Страницы приложения
│   ├── store/             # Zustand state management
│   ├── data/              # Словарь и предложения (для демо)
│   ├── utils/             # SRS логика, storage helpers
│   └── types.ts           # TypeScript типы
│
└── backend/               # Backend (Python + FastAPI)
    ├── routes/            # API endpoints
    ├── models.py          # SQLAlchemy models
    ├── schemas.py         # Pydantic schemas
    ├── auth.py            # JWT + password hashing
    ├── srs.py             # SRS алгоритм
    ├── llm_client.py      # GigaChat клиент
    └── alembic/           # Database migrations
```

## Быстрый старт

### Frontend (демо-режим с localStorage)

```bash
npm install
npm run dev
```

Откройте http://localhost:5173

### Backend (полная версия с PostgreSQL + GigaChat)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Настройте .env
cp .env.example .env
# Заполните DATABASE_URL и GigaChat credentials

# Создайте БД и запустите миграции
createdb wordflow
alembic upgrade head

# Запустите сервер
uvicorn main:app --reload
```

API документация: http://localhost:8000/docs

### Интеграция Frontend + Backend

Создайте `.env` в корне проекта:

```env
VITE_API_URL=http://localhost:8000
```

Frontend автоматически переключится на реальный API.

## Функциональность

### Для пользователя

1. **Регистрация и онбординг**
   - Выбор уровня английского (A1-B2)
   - Автоматическое определение часового пояса

2. **Дашборд**
   - Стрик (дни подряд)
   - Статистика: уроки, выученные слова, слова к повторению
   - CTA: начать/продолжить урок или "лимит достигнут"

3. **Учебный процесс**
   - Превью состава урока (можно исключить слова)
   - Упражнения: перевод предложений с английского на русский
   - Мгновенная обратная связь (правильно/опечатка/неверно)
   - Показ правильного ответа после проверки
   - Блокировка навигации во время урока
   - Автосохранение черновика

4. **Итоги урока**
   - Точность, количество правильных/ошибок
   - Новые слова vs повторение
   - Обновление стрика

5. **Словарь**
   - Список всех изучаемых слов
   - Фильтры по статусу (изучаю/выучено/игнор)
   - Поиск
   - Визуализация SRS стадии

### SRS (Интервальное повторение)

- **7 стадий** (0-6)
- **Интервалы в уроках**: [1, 2, 3, 7, 11, 30]
- **Успех** (correct/typo): stage + 1
- **Ошибка** (incorrect/dont_know): max(stage - 1, 0)
- **Stage 6** → mastered, слово больше не повторяется

### LLM (GigaChat)

**Генерация упражнений:**
- Кластеры по 2-3 слова
- Температура 0.7
- Валидация: нет кириллицы в английском, есть в русском, длина ≤ 200/300

**Оценка переводов:**
- Температура 0.2
- Определение: correct/typo/incorrect
- Извлечение user_fragment
- Защита от инъекций: `<<<UT_{random}>>>`

### Безопасность

- **Пароли**: bcrypt
- **JWT**: короткий TTL (15 мин) + refresh tokens
- **Refresh tokens**: хеш в БД, ротация, family_id
- **Rate limiting**: 10 req/min на auth
- **CORS**: строго по доменам
- **Advisory locks**: защита от параллельного старта уроков

## API Endpoints

### Auth
- `POST /auth/register` — регистрация
- `POST /auth/login` — вход
- `POST /auth/refresh` — обновление токена
- `POST /auth/logout` — выход

### Onboarding
- `POST /onboarding/complete` — завершение онбординга

### Dashboard
- `GET /dashboard/summary` — сводка

### Lesson
- `POST /lesson/preview` — превью урока
- `POST /lesson/new-word/decline` — исключить слово
- `POST /lesson/start` — начать урок (LLM)
- `POST /lesson/evaluate` — оценить перевод (LLM)
- `GET /lesson/{id}/summary` — итоги
- `POST /lesson/{id}/abandon` — прервать

### Vocabulary
- `GET /vocabulary/list` — список слов
- `PATCH /vocabulary/word/{id}/status` — сменить статус

### Admin
- `POST /admin/dictionaries/import` — импорт словаря
- `GET /admin/reports/summary` — отчёт

## Технологии

### Frontend
- React 18 + TypeScript
- Vite (сборка)
- Tailwind CSS (стилизация)
- Zustand (state management)
- React Router (навигация)
- Lucide React (иконки)

### Backend
- Python 3.11+
- FastAPI (async)
- SQLAlchemy 2.0 (async ORM)
- Alembic (миграции)
- PostgreSQL 14+
- Pydantic (валидация)
- python-jose (JWT)
- passlib + bcrypt (пароли)
- httpx (HTTP клиент для GigaChat)

## Лицензия

MIT
