# 🔧 Исправление CORS ошибки

## Проблема
```
The 'Access-Control-Allow-Origin' header has a value 'http://localhost:5173' 
that is not equal to the supplied origin.
```

## Причина
В middleware был баг: когда origin не находился в списке, он возвращал первый из списка (`http://localhost:5173`), а не тот что пришёл в запросе (`http://localhost:3000`).

## Что исправлено

### Backend (`backend/main.py`)
✅ Добавлена проверка: если origin содержит `localhost` или `127.0.0.1`, разрешаем его  
✅ Добавлено логирование для отладки CORS  
✅ Теперь middleware возвращает правильный origin

## Как проверить

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Проверьте логи при запуске
В терминале backend должны увидеть:
```
Starting WordFlow backend...
INFO:     Application startup complete.
```

### 3. Попробуйте войти
- Откройте http://localhost:3000
- Войдите с email и паролем
- Откройте DevTools (F12) → Console

### 4. Проверьте логи backend
При запросе login должны увидеть:
```
📨 OPTIONS /auth/login from 127.0.0.1
🌐 CORS check - Origin: 'http://localhost:3000', Allowed: ['http://localhost:5173', 'http://localhost:3000', ...]
   ✅ Allowing localhost origin: http://localhost:3000
🔧 OPTIONS preflight → 200 (origin: http://localhost:3000, allow: http://localhost:3000)

📨 POST /auth/login from 127.0.0.1
🌐 CORS check - Origin: 'http://localhost:3000', Allowed: [...]
   ✅ Allowing localhost origin: http://localhost:3000
📝 Login request received: user@example.com
🍪 Setting refresh token cookie for user 1
📤 POST /auth/login → 200
```

## Проверка настроек

### Файл `backend/.env`
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173","http://127.0.0.1:3000"]
```

### Файл `backend/config.py`
```python
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
```

## Если проблема не решена

### Проверьте что backend перезапущен
```bash
# Остановите backend (Ctrl+C) и запустите снова
cd backend
uvicorn main:app --reload
```

### Проверьте логи
В терминале backend должны увидеть строки:
```
🌐 CORS check - Origin: 'http://localhost:3000'
```

Если видите другую строку origin, добавьте её в `backend/.env`:
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://localhost:3001","http://127.0.0.1:5173","http://127.0.0.1:3000"]
```

### Проверьте что frontend на правильном порту
```bash
# В терминале frontend должно быть:
Local:   http://localhost:3000/
```

Если frontend на другом порту, добавьте его в CORS_ORIGINS.

## Очистка кэша браузера

Иногда браузер кэширует CORS ответы:
1. Откройте DevTools (F12)
2. Правый клик на кнопке обновления → **Очистить кэш и жёсткая перезагрузка**
3. Или: Ctrl+Shift+Delete → Очистить кэш

## Проверка в Network tab

1. Откройте DevTools (F12) → Network
2. Попробуйте войти
3. Найдите запрос `/auth/login`
4. Проверьте Response Headers:
   ```
   access-control-allow-origin: http://localhost:3000
   access-control-allow-credentials: true
   ```

Если видите `access-control-allow-origin: http://localhost:5173` — backend не перезапущен.

## Итог

После перезапуска backend CORS должен работать корректно. Если проблема сохраняется:
1. Покажите логи backend (особенно строки с `🌐 CORS check`)
2. Покажите Response Headers из Network tab
3. Убедитесь что frontend на порту 3000
