# ✅ Исправлена проблема с JWT токенами

## Что было не так

При попытке оценить упражнение получали ошибку 401 Unauthorized, потому что:
1. Cookie с refresh token устанавливался с `secure=True` (только HTTPS), но мы работаем на HTTP
2. Frontend не передавал cookies с запросами

## Что исправлено

### Backend
- ✅ Изменён `secure=True` на `secure=False` для localhost
- ✅ Добавлено логирование refresh процесса

### Frontend
- ✅ Добавлен `credentials: 'include'` во все fetch запросы
- ✅ Добавлено логирование refresh процесса

## Как проверить

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
В терминале backend при login:
```
🔑 Login request received: user@example.com
🍪 Setting refresh token cookie for user 1
```

### 5. Попробуйте оценить упражнение
Теперь должно работать! Если access token истечёт (через 30 минут), он автоматически обновится.

## Быстрое тестирование

Для быстрого тестирования можно уменьшить время жизни access token:

Откройте `backend/.env` и измените:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=1  # 1 минута для тестирования
```

Перезапустите backend и подождите 1 минуту. При следующем запросе увидите в консоли:
```
📥 API Response: 401 Unauthorized
🔄 Attempting to refresh token...
✅ Token refreshed successfully
```

## Документация

Полная инструкция: `docs/FIX_JWT_TOKENS.md`

## Важно для production

Перед деплоем на production измените обратно на `secure=True`:

```python
# backend/routes/auth.py
secure=True  # Только HTTPS
```

Или сделайте настраиваемым через переменную окружения.
