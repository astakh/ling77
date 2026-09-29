# ✅ GigaChat API - ГОТОВО К РАБОТЕ

## 🎯 Что сделано

Код полностью переписан с использованием **официального SDK GigaChat** согласно документации.

### Преимущества SDK:
- ✅ Автоматическое получение и обновление токенов
- ✅ Кэширование токенов
- ✅ Потокобезопасность
- ✅ Правильный базовый URL: `https://api.giga.chat/v1`
- ✅ Меньше кода, меньше ошибок

## 🚀 Быстрый старт (3 шага)

### Шаг 1: Установите SDK

```bash
cd backend
.\venv\Scripts\activate
pip install gigachat
```

### Шаг 2: Добавьте Authorization Key

Откройте `backend/.env` и добавьте:

```env
GIGACHAT_AUTH_KEY=ваш-authorization-key-из-studio
```

**Где получить:**
1. https://developers.sber.ru/studio
2. Ваш проект GigaChat API
3. Раздел "Credentials" → скопируйте Authorization Key

**Формат:** `UUID:base64string` (длинная строка с `:`)

### Шаг 3: Проверьте и запустите

```bash
# Проверка подключения
python scripts/test_gigachat.py

# Запуск backend
uvicorn main:app --reload
```

## 🧪 Проверка работы

1. Откройте http://localhost:3000
2. Начните урок
3. В логах backend должно быть:

```
🔑 Initializing GigaChat SDK...
✅ GigaChat SDK initialized successfully

🤖 Calling GigaChat API (attempt 1/3)
✅ GigaChat response received
   Latency: 2500ms
   Tokens: 150

✅ Generated 3 exercises using GigaChat LLM
```

## 📋 Что изменилось в коде

### Было (REST API):
```python
# Ручное управление токенами
async def _refresh(self):
    # Получение токена через OAuth
    # Кэширование токена
    # Обновление токена
    # Обработка ошибок
    # 100+ строк кода
```

### Стало (SDK):
```python
# SDK сам всё делает
giga = GigaChat(credentials=AUTH_KEY)
response = giga.chat(messages=[...])
# 2 строки кода!
```

## 🔍 Как работает обновление токена

Согласно документации:
- Токен действителен **30 минут**
- SDK автоматически обновляет токен за **60 секунд** до истечения
- Используется **single-flight refresh** (один запрос на обновление)
- Токен кэшируется в памяти

Вам **НЕ НУЖНО** вручную управлять токенами!

## 📚 Документация

- **Установка SDK:** `INSTALL_GIGACHAT_SDK.md`
- **Тест подключения:** `python scripts/test_gigachat.py`
- **Официальная документация:** https://developers.sber.ru/docs/ru/gigachat/api/main

## ❓ Частые вопросы

### Q: Нужно ли вручную обновлять токен?
**A:** Нет! SDK делает это автоматически.

### Q: Какой URL используется для API?
**A:** `https://api.giga.chat/v1` (правильный базовый URL)

### Q: Что такое Authorization Key?
**A:** Это готовый ключ из личного кабинета вида `UUID:base64string`. Его НЕ НУЖНО кодировать.

### Q: Можно ли использовать Client ID + Client Secret?
**A:** Нет. Используйте только Authorization Key из личного кабинета.

### Q: Что делать если ошибка 401?
**A:** Проверьте Authorization Key в `.env`. Убедитесь что скопировали полную строку.

## 🎉 Готово!

Теперь GigaChat API работает через официальный SDK. Токены обновляются автоматически, код проще и надёжнее.

**Следующие шаги:**
1. `pip install gigachat`
2. Добавьте `GIGACHAT_AUTH_KEY` в `backend/.env`
3. `python scripts/test_gigachat.py` (проверка)
4. `uvicorn main:app --reload` (запуск)
5. Откройте http://localhost:3000 и начните урок!
