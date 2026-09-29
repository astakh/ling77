# 🔧 Исправление ошибок GigaChat SDK

## ❌ Ошибки которые были

### Ошибка 1: `verify_certs` не поддерживается
```
GigaChat: unknown kwargs - {'verify_certs': False}
```

**Причина:** Неправильное имя параметра

**Исправление:** Заменено на `verify_ssl_certs=False`

### Ошибка 2: `messages` не принимается
```
ChatNamespace.__call__() got an unexpected keyword argument 'messages'
```

**Причина:** SDK использует другой API — нужно передавать объект `Chat`, а не keyword arguments

**Исправление:**
```python
# БЫЛО (неправильно):
response = giga.chat(
    messages=[...],
    temperature=0.7,
    max_tokens=2000,
)

# СТАЛО (правильно):
from gigachat.models import Chat, Messages

response = giga.chat(
    Chat(
        messages=[
            Messages(role="system", content="..."),
            Messages(role="user", content="..."),
        ],
        temperature=0.7,
        max_tokens=2000,
    )
)
```

## ✅ Что исправлено

### Файл: `backend/llm_client.py`

1. ✅ Заменён параметр `verify_certs` на `verify_ssl_certs`
2. ✅ Добавлен импорт моделей: `from gigachat.models import Chat, Messages`
3. ✅ Исправлен вызов `giga.chat()` — теперь передаётся объект `Chat`
4. ✅ Добавлена детальная обработка ошибок ответа
5. ✅ Добавлено логирование структуры ответа

### Файл: `backend/scripts/test_gigachat.py`

1. ✅ Обновлён тестовый запрос для использования правильного API
2. ✅ Добавлена проверка структуры ответа

## 🚀 Как проверить

### Шаг 1: Перезапустите backend

```bash
cd backend
uvicorn main:app --reload
```

### Шаг 2: Проверьте тестовый скрипт

```bash
python scripts/test_gigachat.py
```

Должно вывести:
```
✅ GigaChat SDK installed successfully
✅ Authorization Key configured
✅ Connection test passed
```

### Шаг 3: Начните урок

1. Откройте http://localhost:3000
2. Начните урок
3. В логах должно быть:

```
🔑 Initializing GigaChat SDK...
   Base URL: https://api.giga.chat/v1
✅ GigaChat SDK initialized successfully

🤖 Calling GigaChat API (attempt 1/3)
   Purpose: generate_exercise
   Temperature: 0.7

📊 Response received
   Response type: ChatCompletion
   Content length: 300 chars
   Tokens: 150

✅ GigaChat response received
   Latency: 2500ms
   Tokens: 150

✅ Generated 3 exercises using GigaChat LLM
```

## 📋 Правильный API SDK

### Создание клиента
```python
from gigachat import GigaChat

giga = GigaChat(
    credentials="ваш-authorization-key",
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,  # Для тестирования
)
```

### Простой вызов (строка)
```python
response = giga.chat("Привет!")
```

### Полный вызов (объект Chat)
```python
from gigachat.models import Chat, Messages

response = giga.chat(
    Chat(
        messages=[
            Messages(role="system", content="Ты помощник"),
            Messages(role="user", content="Привет!"),
        ],
        temperature=0.7,
        max_tokens=2000,
    )
)
```

### Извлечение ответа
```python
content = response.choices[0].message.content
tokens = response.usage.total_tokens
```

## 🔍 Структура ответа

Ответ SDK имеет структуру:
```python
response.choices[0].message.content  # Текст ответа
response.usage.total_tokens          # Количество токенов
response.model                       # Название модели
```

## ❓ Частые вопросы

### Q: Почему `verify_ssl_certs=False`?
**A:** Для тестирования без сертификата НУЦ Минцифры. В production нужно установить сертификат и использовать `verify_ssl_certs=True`.

### Q: Можно ли использовать простой вызов `giga.chat("text")`?
**A:** Да, но тогда нельзя задать temperature, max_tokens и system prompt. Для нашего приложения нужен полный вызов с объектом `Chat`.

### Q: Что если ответ пустой?
**A:** Проверьте логи — добавлена детальная обработка ошибок. Если `response.choices` пустой, будет выведена ошибка.

## 📚 Документация

- **SDK на GitHub:** https://github.com/ai-forever/gigachat
- **Примеры:** https://github.com/ai-forever/gigachat/blob/main/examples/README.md
- **Официальная документация:** https://developers.sber.ru/docs/ru/gigachat/api/main

## ✅ Готово!

Все ошибки исправлены. Перезапустите backend и проверьте работу!
