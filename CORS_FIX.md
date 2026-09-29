# 🔧 Исправление CORS проблемы

## Что было сделано

1. **Добавлен прокси в Vite** - все запросы к `/api/*` теперь проксируются на `http://localhost:8000`
2. **Обновлен .env** - `VITE_API_URL=/api` (использует прокси вместо прямого запроса)
3. **Добавлено логирование** - в backend и frontend для отладки
4. **Упрощен CORS** - временно разрешены все origins (`allow_origins=["*"]`)

## Как перезапустить

### Backend (в терминале backend)
```bash
# Остановите текущий процесс (Ctrl+C)
# Затем запустите снова:
uvicorn main:app --reload
```

### Frontend (в терминале frontend)
```bash
# Остановите текущий процесс (Ctrl+C)
# Затем запустите снова:
npm run dev
```

## Как проверить

1. Откройте http://localhost:3000
2. Откройте DevTools (F12) → Console
3. Попробуйте зарегистрироваться
4. Смотрите логи:
   - В консоли браузера: `🌐 API Request: POST /api/auth/register`
   - В терминале backend: `📨 POST /auth/register from 127.0.0.1`

## Что должно быть в логах

### Frontend Console
```
🌐 API Request: POST /api/auth/register
📥 API Response: 200 OK
```

### Backend Terminal
```
📨 POST /auth/register from 127.0.0.1
📝 Register request received: test@example.com
📤 POST /auth/register → 200
```

## Если всё ещё не работает

### Проверьте:
1. Backend запущен на порту 8000?
   ```bash
   curl http://localhost:8000/health
   ```
   Должно вернуть: `{"status":"ok","service":"wordflow"}`

2. Frontend запущен на порту 3000?
   - Откройте http://localhost:3000

3. Прокси работает?
   - В консоли браузера должно быть: `POST /api/auth/register` (не `http://localhost:8000/auth/register`)

### Попробуйте:
1. Очистите кэш браузера (Ctrl+Shift+R)
2. Перезапустите оба сервера
3. Проверьте, что .env файл создан в корне проекта

## Альтернативное решение (если прокси не помогает)

Если прокси не работает, можно вернуть прямые запросы и исправить CORS в backend:

1. Измените `.env`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

2. В `backend/main.py` убедитесь, что CORS настроен правильно:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Перезапустите оба сервера
