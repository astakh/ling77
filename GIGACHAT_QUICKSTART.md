# 🔑 Быстрая настройка GigaChat API

## 📋 Что нужно сделать

### 1. Получить credentials

1. Перейдите на https://developers.sber.ru/studio
2. Войдите или зарегистрируйтесь
3. Создайте проект "GigaChat API"
4. Скопируйте **Client ID** и **Client Secret**

### 2. Настроить .env

Откройте `backend/.env` и добавьте:

```env
# GigaChat API credentials
GIGACHAT_CLIENT_ID=your-client-id-here
GIGACHAT_CLIENT_SECRET=your-client-secret-here
```

### 3. Перезапустить backend

```bash
cd backend
uvicorn main:app --reload
```

### 4. Проверить

1. Откройте http://localhost:3000
2. Начните урок
3. В логах backend должно быть:
   ```
   ✅ Generated 3 exercises using GigaChat LLM
   ```

## ⚠️ Если не работает

### Ошибка: "credentials doesn't match db data"

**Решение:** Проверьте что скопировали правильные Client ID и Client Secret (не Authorization Key).

### Ошибка: "GigaChat credentials not configured"

**Решение:** Добавьте credentials в `backend/.env` и перезапустите backend.

### Ошибка: "503 Service Unavailable"

**Решение:** 
1. Проверьте что credentials настроены
2. Проверьте что GigaChat API доступен
3. Если API недоступен, подождите и попробуйте позже
4. Frontend покажет: "Сервис временно недоступен. Попробуйте позже."

## 📚 Подробная документация

- [Настройка GigaChat API](./docs/GIGACHAT_SETUP.md) - полная инструкция
- [Обработка ошибок LLM](./docs/LLM_ERROR_HANDLING.md) - что делать при ошибках

## 🎯 Важно

**Без GigaChat API приложение не работает!** 

GigaChat используется для:
- Генерации упражнений (предложений с целевыми словами)
- Оценки переводов пользователя

Если GigaChat недоступен, пользователи увидят сообщение "Сервис временно недоступен. Попробуйте позже."
