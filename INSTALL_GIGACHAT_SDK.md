# 🚀 Установка GigaChat SDK и настройка

## ⚠️ ВАЖНО: Установите официальный SDK GigaChat

Согласно документации, рекомендуется использовать официальный SDK вместо REST API.

### Шаг 1: Установите SDK

```bash
cd backend
.\venv\Scripts\activate  # Windows
# или source venv/bin/activate  # Linux/Mac

pip install gigachat
```

### Шаг 2: Получите Authorization Key

1. Перейдите на https://developers.sber.ru/studio
2. Откройте ваш проект GigaChat API
3. Найдите раздел **"Credentials"** или **"Авторизация"**
4. Скопируйте **Authorization Key** (длинная строка вида `UUID:base64string`)

**Пример формата:**
```
01a07acf-911d-76cc-a7d4-36d5190004f5:MDfhMDdhY2YtOTExZC03NmNjLWE3ZDQtMzZkNTE5MDAwNGY1...
```

### Шаг 3: Добавьте в backend/.env

Откройте `backend/.env` и добавьте:

```env
# GigaChat API
# Authorization Key из личного кабинета Studio
GIGACHAT_AUTH_KEY=01a07acf-911d-76cc-a7d4-36d5190004f5:MDfhMDdhY2Yt...
```

**ВАЖНО:**
- Используйте **Authorization Key** целиком (включая UUID и base64 часть)
- НЕ разделяйте на Client ID и Client Secret
- НЕ кодируйте в base64 ещё раз

### Шаг 4: Перезапустите backend

```bash
uvicorn main:app --reload
```

### Шаг 5: Проверьте логи

При запуске урока в логах должно быть:

```
🔑 Initializing GigaChat SDK...
   Base URL: https://api.giga.chat/v1
   Auth Key preview: 01a07acf-911d-76cc-a7d4...
✅ GigaChat SDK initialized successfully

🤖 Calling GigaChat API (attempt 1/3)
   Purpose: generate_exercise
   Temperature: 0.7
   Prompt length: 500 chars

✅ GigaChat response received
   Latency: 2500ms
   Tokens: 150
   Response length: 300 chars

✅ Generated 3 exercises using GigaChat LLM
```

## 🔍 Как работает SDK

Официальный SDK `gigachat` автоматически:
- ✅ Получает токен доступа при первом запросе
- ✅ Кэширует токен в памяти
- ✅ Обновляет токен за 60 секунд до истечения
- ✅ Использует правильный базовый URL: `https://api.giga.chat/v1`
- ✅ Управляет блокировками при многопоточности

Вам **НЕ НУЖНО** вручную управлять токенами!

## 🧪 Проверка установки

Выполните тестовый скрипт:

```bash
cd backend
python scripts/test_gigachat.py
```

Должно вывести:
```
✅ GigaChat SDK installed successfully
✅ Authorization Key configured
✅ Connection test passed
```

## ❌ Частые ошибки

### Ошибка: "gigachat package not installed"

**Решение:**
```bash
pip install gigachat
```

### Ошибка: "GigaChat credentials not configured"

**Решение:**
1. Откройте `backend/.env`
2. Добавьте `GIGACHAT_AUTH_KEY=...`
3. Перезапустите backend

### Ошибка: "401 Unauthorized" или "credentials doesn't match"

**Причина:** Неправильный Authorization Key

**Решение:**
1. Скопируйте Authorization Key заново из личного кабинета
2. Убедитесь что скопировали полную строку (не обрезали)
3. Проверьте что нет лишних пробелов в `.env`

### Ошибка: "SSLCertVerificationError"

**Причина:** Сертификат НУЦ Минцифры не установлен

**Решение:**
- Для разработки: SDK использует `verify_certs=False` (уже настроено)
- Для production: установите сертификат НУЦ Минцифры

## 📚 Документация

- **Официальная документация GigaChat:** https://developers.sber.ru/docs/ru/gigachat/api/main
- **SDK на PyPI:** https://pypi.org/project/gigachat/
- **Быстрый старт:** https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api

## 💡 Преимущества SDK

| REST API | SDK |
|----------|-----|
| Нужно вручную получать токен | ✅ Токен обновляется автоматически |
| Нужно кэшировать токен | ✅ Кэширование встроено |
| Нужно управлять блокировками | ✅ Потокобезопасность встроена |
| Нужно обрабатывать ошибки | ✅ Обработка ошибок встроена |
| Больше кода | ✅ Меньше кода |

**Рекомендация:** Всегда используйте SDK для production.
