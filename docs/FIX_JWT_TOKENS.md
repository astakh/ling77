# 🔐 Исправление проблемы с JWT токенами

## Проблема
При попытке оценить упражнение получали ошибку 401 Unauthorized:
```
POST /lesson/evaluate → 401 Unauthorized
POST /auth/refresh → 401 Unauthorized
```

## Причина
1. **Cookie с `secure=True`**: Refresh token устанавливался в cookie с флагом `secure=True`, что означает передачу только по HTTPS. Но мы работаем на localhost с HTTP.
2. **Отсутствие `credentials: 'include'`**: Frontend не передавал cookies с запросами, поэтому refresh token не доходил до backend.

## Что исправлено

### Backend (`backend/routes/auth.py`)
1. ✅ Изменён `secure=True` на `secure=False` в login endpoint (строка 120)
2. ✅ Изменён `secure=True` на `secure=False` в refresh endpoint (строка 180)
3. ✅ Добавлено подробное логирование в refresh endpoint

### Frontend (`src/api/client.ts`)
1. ✅ Добавлен `credentials: 'include'` в функцию `refreshToken()` (строка 28)
2. ✅ Добавлен `credentials: 'include'` в основной `request()` (строка 57)
3. ✅ Добавлен `credentials: 'include'` в повторный запрос после refresh (строка 76)
4. ✅ Добавлено логирование процесса refresh

## Как работает refresh token

### Поток авторизации:
1. **Login/Register**: Backend устанавливает refresh token в httpOnly cookie
2. **Каждый запрос**: Frontend передаёт cookie с `credentials: 'include'`
3. **Access token истекает** (через 30 минут): Frontend получает 401
4. **Refresh**: Frontend вызывает `/auth/refresh` с cookie
5. **Backend**: Проверяет refresh token, выдаёт новый access token
6. **Retry**: Frontend повторяет исходный запрос с новым access token

### Время жизни токенов:
- **Access token**: 30 минут (`ACCESS_TOKEN_EXPIRE_MINUTES=30`)
- **Refresh token**: 30 дней (`REFRESH_TOKEN_EXPIRE_DAYS=30`)

## Как тестировать

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Перезапустите frontend
```bash
npm run dev
```

### 3. Войдите в систему
- Откройте http://localhost:3000
- Войдите или зарегистрируйтесь
- Откройте DevTools (F12) → Application → Cookies
- Должны увидеть cookie `refresh_token`

### 4. Проверьте логи
В терминале backend при login должны быть логи:
```
🔑 Login request received: user@example.com
🍪 Setting refresh token cookie for user 1
```

### 5. Подождите 30 минут (или измените ACCESS_TOKEN_EXPIRE_MINUTES)
Для быстрого тестирования можно временно уменьшить время жизни access token:
```env
# backend/.env
ACCESS_TOKEN_EXPIRE_MINUTES=1  # 1 минута для тестирования
```

### 6. Попробуйте выполнить действие
- Начните урок
- Попробуйте оценить упражнение
- В консоли браузера должны увидеть:
```
📥 API Response: 401 Unauthorized
🔄 Attempting to refresh token...
🔄 Refresh response: 200
✅ Token refreshed successfully
📥 API Response: 200 OK
```

В терминале backend:
```
🔄 Refresh token request received
✅ Refresh token found (length: 64)
   Token hash: abc123...
✅ Valid refresh token found for user 1
🍪 Setting new refresh token cookie for user 1
```

## Проверка cookies в браузере

### Chrome/Edge:
1. F12 → Application → Cookies → localhost:3000
2. Должны увидеть:
   - `refresh_token`: длинная строка
   - HttpOnly: ✓
   - Secure: ✗ (должно быть выключено для localhost)
   - SameSite: Lax

### Firefox:
1. F12 → Storage → Cookies → localhost:3000
2. Проверьте те же параметры

## Если проблема не решена

### Проверьте что cookie устанавливается
В терминале backend при login должны быть логи:
```
🍪 Setting refresh token cookie for user X
```

### Проверьте что cookie передаётся
В DevTools → Network → найдите запрос `/auth/refresh`:
- Request Headers должны содержать: `Cookie: refresh_token=...`

### Проверьте БД
```sql
SELECT id, user_id, token_hash, is_revoked, expires_at 
FROM refresh_tokens 
WHERE user_id = 1 
ORDER BY created_at DESC 
LIMIT 5;
```

Должны быть записи с `is_revoked = false` и `expires_at` в будущем.

## Production vs Development

### Development (localhost):
```python
secure=False  # HTTP
samesite="lax"
```

### Production (HTTPS):
```python
secure=True  # HTTPS только
samesite="strict"  # или "none" с secure=True
```

Можно сделать настраиваемым через переменную окружения:
```python
# backend/config.py
COOKIE_SECURE: bool = False  # True для production

# backend/routes/auth.py
secure=settings.COOKIE_SECURE,
```

## Дополнительные улучшения

### 1. Увеличить время жизни access token
```env
# backend/.env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 час вместо 30 минут
```

### 2. Добавить автоматический refresh перед истечением
Можно добавить в frontend проверку времени истечения токена и автоматический refresh за 5 минут до истечения.

### 3. Использовать secure cookies в production
Добавить в `backend/.env`:
```env
COOKIE_SECURE=True
```

И использовать в `auth.py`:
```python
secure=settings.COOKIE_SECURE,
```

## Ссылки
- [MDN: HTTP Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
- [FastAPI: Cookies](https://fastapi.tiangolo.com/tutorial/response-model/#response_model_encoding_parameters)
