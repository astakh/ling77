# 🔧 Финальное исправление CORS

## Что изменилось

1. **Убран CORSMiddleware** - заменён на простой middleware с ручными заголовками
2. **Убран credentials: 'include'** - может конфликтовать с CORS
3. **Упрощена конфигурация** - максимально открытые настройки CORS
4. **Добавлено логирование** - для отладки

## Инструкция по перезапуску

### Шаг 1: Остановите оба сервера

В обоих терминалах нажмите `Ctrl+C`

### Шаг 2: Перезапустите backend

```bash
cd backend
uvicorn main:app --reload
```

Должны увидеть:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Шаг 3: Перезапустите frontend

```bash
npm run dev
```

Должны увидеть:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### Шаг 4: Проверьте CORS

Откройте новый терминал и выполните:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/auth/register -Method OPTIONS -Headers @{"Origin"="http://localhost:3000"} | Select-Object -ExpandProperty Headers
```

**Linux/Mac:**
```bash
curl -I -X OPTIONS http://localhost:8000/auth/register -H "Origin: http://localhost:3000"
```

Должны увидеть заголовки:
```
access-control-allow-origin: *
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: *
```

### Шаг 5: Откройте браузер

1. Откройте http://localhost:3000
2. Нажмите `Ctrl+Shift+R` (очистить кэш)
3. Откройте DevTools (F12) → Console
4. Попробуйте зарегистрироваться

## Ожидаемые логи

### В консоли браузера:
```
🌐 API Request: POST http://localhost:8000/auth/register
📥 API Response: 200 OK from http://localhost:8000/auth/register
```

### В терминале backend:
```
📨 OPTIONS /auth/register from 127.0.0.1
🔧 OPTIONS request for /auth/register
📤 OPTIONS /auth/register → 200
📨 POST /auth/register from 127.0.0.1
📝 Register request received: your@email.com
📤 POST /auth/register → 200
```

## Если всё ещё не работает

### Вариант 1: Проверьте что backend получает OPTIONS

В терминале backend должны видеть строку:
```
🔧 OPTIONS request for /auth/register
```

Если её нет - значит OPTIONS запрос не доходит до backend.

### Вариант 2: Проверьте firewall

```bash
# Windows
netsh advfirewall firewall show rule name=all | findstr 8000

# Linux/Mac
sudo ufw status
```

Порт 8000 должен быть открыт.

### Вариант 3: Попробуйте другой браузер

Откройте http://localhost:3000 в другом браузере (Chrome, Firefox, Edge).

### Вариант 4: Проверьте что нет других процессов на порту 8000

```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Если есть другие процессы - убейте их.

## Крайний случай: Используйте прокси

Если ничего не помогает, верните прокси в `vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "0.0.0.0",
    port: 3000,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

И измените `src/api/client.ts`:
```typescript
const API_BASE_URL = '/api';
```

Перезапустите frontend: `npm run dev`

## Проверочный скрипт

Запустите:
```bash
bash check_cors.sh
```

Или в PowerShell:
```powershell
.\check_cors.sh
```

## Что делать если ничего не помогло

Напишите мне:
1. Логи backend (полный вывод терминала)
2. Логи frontend (Console в DevTools)
3. Результат команды `curl -I -X OPTIONS http://localhost:8000/auth/register`
4. Скриншот ошибки в браузере
