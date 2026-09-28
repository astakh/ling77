# 🚀 Запуск полного стека WordFlow (Frontend + Backend)

## ✅ Что реализовано

Фронтенд полностью подключен к реальному backend через API:
- ✅ Авторизация (регистрация/вход) с JWT токенами
- ✅ Онбординг (выбор уровня)
- ✅ Dashboard со статистикой из БД
- ✅ Превью урока (подбор слов из БД)
- ✅ Начало урока (создание в БД)
- ✅ Оценка упражнений (через backend)
- ✅ Завершение урока
- ✅ Словарь (пагинация, фильтры, смена статуса)
- ✅ Словари (выбор активного словаря)
- ✅ Автоматический refresh JWT токенов

---

## 🎯 Пошаговый запуск

### Шаг 1. Запустить backend

В терминале VSCode (первый терминал):

```powershell
cd D:\ling77\backend
.\venv\Scripts\activate
uvicorn main:app --reload
```

Ожидается:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

Проверьте: http://localhost:8000/docs — должна открыться Swagger документация.

### Шаг 2. Запустить frontend

Откройте **второй терминал** в VSCode (`Ctrl+Shift+` `):

```powershell
cd D:\ling77
npm run dev
```

Ожидается:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Шаг 3. Открыть приложение

Перейдите на **http://localhost:5173**

---

## 🧪 Тестирование полного цикла

### 1. Регистрация

1. Откройте http://localhost:5173
2. Нажмите **«Создать аккаунт»**
3. Введите email (например, `test@example.com`) и пароль (мин. 6 символов)
4. Нажмите **«Создать аккаунт»**

**Что происходит:**
- Frontend → `POST /auth/register` → Backend создаёт пользователя в PostgreSQL
- JWT токен сохраняется в localStorage
- Перенаправление на онбординг

### 2. Онбординг

1. Выберите уровень (A1, A2, B1 или B2)
2. Нажмите **«Начать обучение»**

**Что происходит:**
- Frontend → `POST /onboarding/complete` → Backend создаёт профиль обучения
- Привязывается словарь по умолчанию

### 3. Dashboard

Вы увидите:
- Стрик (пока 0)
- Статистику (уроки, выучено, к повторению)
- Кнопку **«Начать урок»**

**Что происходит:**
- Frontend → `GET /dashboard/summary` → Backend возвращает данные из БД

### 4. Превью урока

1. Нажмите **«Начать урок»**
2. Увидите список слов для урока
3. Можете исключить слова (кнопка ✕)

**Что происходит:**
- Frontend → `POST /lesson/preview` → Backend подбирает слова из словаря

### 5. Начало урока

1. Нажмите **«Начать урок»**
2. Увидите первое упражнение

**Что происходит:**
- Frontend → `POST /lesson/start` → Backend:
  - Подбирает слова (due + new)
  - Группирует в кластеры
  - (В будущем) Вызывает GigaChat для генерации предложений
  - Создаёт урок в БД

### 6. Упражнение

1. Переведите предложение на русский
2. Нажмите **«Проверить»** или **«Не знаю»**
3. Увидите результат (правильно/опечатка/неверно)
4. Нажмите **«Далее»**

**Что происходит:**
- Frontend → `POST /lesson/evaluate` → Backend:
  - (В будущем) Вызывает GigaChat для оценки
  - Обновляет SRS стадии слов
  - Если последнее упражнение → автоматически завершает урок

### 7. Завершение урока

После последнего упражнения:
1. Нажмите **«Завершить урок»**
2. Увидите итоги (точность, новые слова, повторение)

**Что происходит:**
- Backend обновляет статус урока на `completed`
- Обновляется стрик

### 8. Словарь

1. На дашборде нажмите иконку **📚 Словари**
2. Увидите список доступных словарей
3. Можете выбрать другой словарь

**Что происходит:**
- Frontend → `GET /dictionaries` → Backend возвращает список словарей
- Frontend → `GET /dictionaries/profile/current` → текущий словарь
- Frontend → `PATCH /dictionaries/profile/dictionary` → смена словаря

### 9. Мои слова

1. На дашборде нажмите иконку **📝 Мои слова**
2. Увидите все изученные слова
3. Можете фильтровать, искать, менять статус

**Что происходит:**
- Frontend → `GET /vocabulary/list` → Backend возвращает слова из `user_words`
- Frontend → `PATCH /vocabulary/word/{id}/status` → смена статуса

---

## 🔍 Проверка в базе данных

Подключитесь к PostgreSQL:

```bash
psql -h your-server-ip -U wordflow_user -d wordflow
```

Проверьте данные:

```sql
-- Пользователи
SELECT id, email, is_onboarded FROM users;

-- Профили
SELECT user_id, level, dictionary_id, last_lesson_number FROM learning_profiles;

-- Уроки
SELECT id, learning_profile_id, lesson_number, status, started_local_date FROM lessons;

-- Упражнения
SELECT id, lesson_id, order_index, status FROM lesson_exercises;

-- Слова пользователя
SELECT learning_profile_id, word_id, status, stage, due_lesson_number FROM user_words;
```

---

## 🛠️ Отладка

### Если frontend не подключается к backend

1. Проверьте, что backend запущен:
   ```bash
   curl http://localhost:8000/health
   ```
   Ожидается: `{"status":"ok","service":"wordflow"}`

2. Проверьте CORS в `backend/.env`:
   ```env
   CORS_ORIGINS=["http://localhost:5173"]
   ```

3. Проверьте `src/.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. Откройте DevTools (F12) → вкладка Network → посмотрите запросы

### Если ошибка 401 Unauthorized

- JWT токен истёк (15 минут)
- Frontend автоматически пытается refresh через `POST /auth/refresh`
- Если refresh не работает → перенаправляет на `/auth`

### Если ошибка 503 Service Unavailable

- Backend не может подключиться к GigaChat
- Проверьте credentials в `backend/.env`
- Для теста можно закомментировать вызовы LLM в `backend/routes/lesson.py`

---

## 📊 Архитектура взаимодействия

```
┌─────────────┐
│  Frontend   │  React + TypeScript
│  Port 5173  │
└──────┬──────┘
       │ HTTP (JSON)
       │ JWT Auth (Bearer token)
       ▼
┌─────────────┐
│   Backend   │  FastAPI + SQLAlchemy
│  Port 8000  │
└──────┬──────┘
       │ Async SQL
       ▼
┌─────────────┐
│ PostgreSQL  │  Remote server
│  Port 5432  │
└─────────────┘
```

---

## 🎉 Готово!

Теперь у вас работает полноценное приложение:
- **Frontend** на React с реальным UI/UX
- **Backend** на FastAPI с PostgreSQL
- **JWT аутентификация** с автоматическим refresh
- **SRS алгоритм** для интервального повторения
- **Множественные словари** с возможностью выбора

Все данные сохраняются в PostgreSQL и доступны через API.
