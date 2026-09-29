# 🚀 Инструкция по запуску WordFlow в VSCode

## 📋 Требования

- **VSCode** (последняя версия)
- **Python 3.11+**
- **Node.js 18+** и **npm**
- **PostgreSQL 14+** (у вас на удалённом сервере ✓)
- **Git**

## 🔧 Рекомендуемые расширения VSCode

При открытии проекта VSCode предложит установить расширения из `.vscode/extensions.json`:

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- ES7+ React snippets (dsznajder.es7-react-js-snippets)
- DotENV (mikestead.dotenv)
- SQLTools + PostgreSQL driver (mtxr.sqltools)

---

## 🗄️ Шаг 1: Создание базы данных на удалённом сервере

### Вариант A: Через psql (рекомендуется)

Подключитесь к удалённому серверу:

```bash
psql -h your-server-ip -U postgres -p 5432
```

Выполните SQL из файла `backend/scripts/create_database.sql`:

```sql
-- 1. Создать БД
CREATE DATABASE wordflow
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- 2. Создать пользователя (опционально)
CREATE ROLE wordflow_user WITH LOGIN PASSWORD 'your_secure_password_here';

-- 3. Выдать права
GRANT ALL PRIVILEGES ON DATABASE wordflow TO postgres;
GRANT ALL PRIVILEGES ON DATABASE wordflow TO wordflow_user;

-- 4. Подключиться к новой БД
\c wordflow

-- 5. Выдать права на схему
GRANT ALL ON SCHEMA public TO wordflow_user;
GRANT ALL ON SCHEMA public TO postgres;
```

### Вариант B: Через pgAdmin или другой GUI

1. Подключитесь к удалённому серверу
2. Создайте новую базу данных `wordflow` (кодировка UTF-8)
3. Создайте пользователя `wordflow_user` с паролем
4. Выдайте все права на БД и схему `public`

### Вариант C: Одной командой (если есть доступ)

```bash
# Создать БД
createdb -h your-server-ip -U postgres wordflow

# Или через psql
psql -h your-server-ip -U postgres -f backend/scripts/create_database.sql
```

### Проверка подключения

```bash
psql -h your-server-ip -U postgres -d wordflow -c "SELECT version();"
```

---

## 🐍 Шаг 2: Настройка Backend

### 2.1. Создать виртуальное окружение

```bash
cd backend
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2.2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2.3. Настроить .env

Создайте файл `backend/.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
# Database - ЗАМЕНИТЕ на ваш удалённый сервер!
DATABASE_URL=postgresql+asyncpg://wordflow_user:your_secure_password@your-server-ip:5432/wordflow

# JWT
SECRET_KEY=generate-random-64-chars-here-use-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# GigaChat (получите на https://developers.sber.ru/)
GIGACHAT_CLIENT_ID=your-client-id
GIGACHAT_CLIENT_SECRET=your-client-secret

# CORS - добавьте домен фронтенда
CORS_ORIGINS=["http://localhost:5173"]
```

**Важно:**
- Замените `your-server-ip` на IP вашего удалённого PostgreSQL сервера
- Замените `your_secure_password` на реальный пароль
- Сгенерируйте `SECRET_KEY`: `openssl rand -hex 32`
- Для GigaChat получите credentials на https://developers.sber.ru/

### 2.4. Запустить миграции

```bash
alembic upgrade head
```

Проверьте, что таблицы созданы:

```bash
psql -h your-server-ip -U postgres -d wordflow -c "\dt"
```

Должны появиться таблицы:
- users
- learning_profiles
- dictionaries
- words
- user_words
- lessons
- lesson_exercises
- lesson_exercise_words
- refresh_tokens
- llm_calls
- events

---

## 🎨 Шаг 3: Настройка Frontend

### 3.1. Установить зависимости

В корне проекта:

```bash
npm install
```

### 3.2. Настроить .env (опционально)

Создайте `.env` в корне проекта:

```env
VITE_API_URL=http://localhost:8000
```

Если backend на другом порту или хосте, укажите правильный URL.

---

## ▶️ Шаг 4: Запуск проекта

### Вариант A: Через VSCode (рекомендуется)

1. Откройте проект в VSCode
2. Нажмите `F5` или перейдите в **Run and Debug** (Ctrl+Shift+D)
3. Выберите конфигурацию **"Full Stack"** из выпадающего списка
4. Нажмите зелёную кнопку ▶️

Это запустит одновременно:
- Backend на http://localhost:8000
- Frontend на http://localhost:5173

### Вариант B: Через терминал

**Терминал 1 — Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Терминал 2 — Frontend:**
```bash
npm run dev
```

### Вариант C: Через VSCode Tasks

1. `Ctrl+Shift+P` → **Tasks: Run Task**
2. Выберите **"Backend: Start server"**
3. Повторите и выберите **"Frontend: Start dev server"**

---

## ✅ Шаг 5: Проверка

### Backend

Откройте http://localhost:8000/docs

Должна появиться Swagger UI с API документацией.

Проверьте health check:

```bash
curl http://localhost:8000/health
```

Ожидается: `{"status":"ok","service":"wordflow"}`

### Frontend

Откройте http://localhost:5173

Должна появиться страница авторизации WordFlow.

---

## 🧪 Шаг 6: Тестирование

### Регистрация пользователя

1. Откройте http://localhost:5173
2. Нажмите "Создать аккаунт"
3. Введите email и пароль (мин. 6 символов)
4. Завершите онбординг (выберите уровень)

### Создание первого урока

1. На дашборде нажмите "Начать урок"
2. Просмотрите состав урока (можно исключить слова)
3. Нажмите "Начать урок"
4. Переведите предложение
5. Получите обратную связь

---

## 🔧 Решение проблем

### Ошибка подключения к БД

**Симптом:** `could not connect to server`

**Решение:**
1. Проверьте, что PostgreSQL запущен на удалённом сервере
2. Проверьте firewall (порт 5432 должен быть открыт)
3. Проверьте `pg_hba.conf` на сервере — разрешены ли подключения с вашего IP
4. Проверьте `postgresql.conf` — `listen_addresses = '*'`

```bash
# Проверить доступность порта
nc -zv your-server-ip 5432
```

### Ошибка миграций

**Симптом:** `relation "users" does not exist`

**Решение:**
```bash
cd backend
alembic upgrade head
```

### Ошибка CORS

**Симптом:** `Access to fetch at ... has been blocked by CORS policy`

**Решение:**
Проверьте `CORS_ORIGINS` в `backend/.env` — должен содержать URL фронтенда.

### Ошибка GigaChat

**Симптом:** `503 Service temporarily unavailable`

**Решение:**
1. Проверьте credentials в `.env`
2. Убедитесь, что доступ к GigaChat API разрешён
3. Проверьте логи backend

### Порт занят

**Симптом:** `Address already in use`

**Решение:**
```bash
# Найти процесс
lsof -i :8000  # или :5173

# Убить процесс
kill -9 <PID>
```

---

## 📝 Полезные команды

### Backend

```bash
# Запустить сервер
uvicorn main:app --reload

# Создать миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Показать статус миграций
alembic current
```

### Frontend

```bash
# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview
```

### Database

```bash
# Подключиться к БД
psql -h your-server-ip -U postgres -d wordflow

# Показать таблицы
\dt

# Выйти
\q
```

---

## 🎯 Структура проекта

```
wordflow/
├── .vscode/              # Настройки VSCode
│   ├── settings.json     # Настройки редактора
│   ├── launch.json       # Конфигурации отладки
│   ├── tasks.json        # Автоматизированные задачи
│   └── extensions.json   # Рекомендуемые расширения
│
├── backend/              # Python FastAPI backend
│   ├── venv/            # Виртуальное окружение (создать)
│   ├── .env             # Переменные окружения (создать)
│   ├── main.py          # Entry point
│   ├── config.py        # Настройки
│   ├── database.py      # SQLAlchemy setup
│   ├── models.py        # DB модели
│   ├── schemas.py       # Pydantic схемы
│   ├── auth.py          # JWT + passwords
│   ├── srs.py           # SRS алгоритм
│   ├── llm_client.py    # GigaChat клиент
│   ├── routes/          # API endpoints
│   ├── alembic/         # Миграции
│   └── scripts/         # SQL скрипты
│
├── src/                 # React frontend
│   ├── api/             # API клиент
│   ├── pages/           # Страницы
│   ├── store/           # Zustand store
│   ├── data/            # Словарь (демо)
│   └── utils/           # Утилиты
│
└── README.md            # Документация
```

---

## 🔐 Безопасность

**Перед деплоем:**

1. ✅ Измените `SECRET_KEY` в `.env`
2. ✅ Используйте сильный пароль для БД
3. ✅ Настройте HTTPS для production
4. ✅ Ограничьте CORS только нужными доменами
5. ✅ Не коммитьте `.env` в git
6. ✅ Используйте переменные окружения для secrets

---

## 📚 Дополнительные ресурсы

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0:** https://docs.sqlalchemy.org/en/20/
- **React:** https://react.dev/
- **Tailwind CSS:** https://tailwindcss.com/
- **GigaChat API:** https://developers.sber.ru/

---

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте логи backend в терминале
2. Проверьте консоль браузера (F12)
3. Убедитесь, что все зависимости установлены
4. Проверьте `.env` конфигурацию
5. Проверьте доступность PostgreSQL

---

**Готово!** 🎉 Проект готов к разработке в VSCode.
