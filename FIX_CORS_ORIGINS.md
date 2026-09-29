# 🔧 Исправление проблемы с CORS_ORIGINS

## Проблема
В логах backend видно:
```
Allowed: ['http://localhost:5173']
```

Хотя в `.env` указано несколько origins. Pydantic-settings не парсит JSON строку из `.env` правильно для `list[str]`.

## Что исправлено

### Файл `backend/config.py`
✅ Добавлен валидатор `parse_cors_origins` который:
- Пытается распарсить строку как JSON
- Если не JSON - разделяет по запятой
- Возвращает список строк

✅ Добавлена проверка после инициализации settings

### Файл `backend/main.py`
✅ Добавлено логирование загруженных `CORS_ORIGINS` при старте

## Как проверить

### 1. Перезапустите backend
```bash
cd backend
# Остановите (Ctrl+C) и запустите снова
uvicorn main:app --reload
```

### 2. Проверьте логи при старте
В терминале backend должны увидеть:
```
Starting WordFlow backend...
📋 CORS_ORIGINS: ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000']
INFO:     Application startup complete.
```

**ВАЖНО:** Должны быть ВСЕ 4 origins, а не только один!

### 3. Попробуйте войти
- Откройте http://localhost:3000
- Войдите с email и паролем
- Откройте DevTools (F12) → Console

### 4. Проверьте логи backend
При запросе login должны увидеть:
```
📨 OPTIONS /auth/login from 127.0.0.1
🌐 CORS check - Origin: 'http://localhost:3000', Allowed: ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000']
   ✅ Allowing localhost origin: http://localhost:3000
🔧 OPTIONS preflight → 200 (origin: http://localhost:3000, allow: http://localhost:3000)
```

## Формат CORS_ORIGINS в .env

### Вариант 1: JSON массив (рекомендуется)
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173","http://127.0.0.1:3000"]
```

### Вариант 2: Строка через запятую
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000
```

Оба варианта теперь работают!

## Если проблема не решена

### Проверьте что backend перезапущен
```bash
# Остановите backend (Ctrl+C)
# Убедитесь что процесс остановлен
# Запустите снова
cd backend
uvicorn main:app --reload
```

### Проверьте логи при старте
Должны увидеть строку:
```
📋 CORS_ORIGINS: ['http://localhost:5173', 'http://localhost:3000', ...]
```

Если видите только один origin - значит `.env` не читается или парсится неправильно.

### Проверьте файл .env
```bash
cd backend
cat .env | grep CORS_ORIGINS
```

Должно вывести:
```
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173","http://127.0.0.1:3000"]
```

### Проверьте что .env в правильной папке
Файл `.env` должен быть в `backend/.env`, а не в корне проекта.

## Очистка кэша браузера

После перезапуска backend:
1. Откройте DevTools (F12)
2. Правый клик на кнопке обновления → **Очистить кэш и жёсткая перезагрузка**
3. Или: Ctrl+Shift+Delete → Очистить кэш

## Итог

После перезапуска backend в логах должны быть ВСЕ 4 origins. Если видите только один - покажите мне:
1. Логи при старте backend (строка с `📋 CORS_ORIGINS`)
2. Содержимое файла `backend/.env` (строку с `CORS_ORIGINS`)
