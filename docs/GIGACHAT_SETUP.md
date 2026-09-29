# 🔑 Настройка GigaChat API

## 📋 Что такое GigaChat?

GigaChat - это LLM (Large Language Model) от Сбера, которая используется в WordFlow для:
- Генерации упражнений (предложений с целевыми словами)
- Оценки переводов пользователя

## 🚀 Как получить credentials

### Шаг 1: Регистрация в Studio

1. Перейдите на https://developers.sber.ru/studio
2. Войдите или зарегистрируйтесь
3. Перейдите в раздел "GigaChat API"

### Шаг 2: Создание проекта

1. Нажмите "Создать проект"
2. Заполните информацию о проекте
3. Выберите тип доступа:
   - **Физические лица** - бесплатный лимит (рекомендуется для разработки)
   - **ИП/Юридические лица** - платные пакеты

### Шаг 3: Получение credentials

После создания проекта вы получите:
- **Client ID** (клиентский идентификатор)
- **Client Secret** (клиентский секрет)
- **Authorization Key** (уже закодированный Base64)

**Важно:** Вам нужны **Client ID** и **Client Secret** (не Authorization Key).

### Шаг 4: Настройка .env

Откройте `backend/.env` и добавьте **Authorization Key** (рекомендуется):

```env
# GigaChat API - Authorization Key из личного кабинета
GIGACHAT_AUTH_KEY=your-authorization-key-from-studio
```

**ИЛИ** используйте Client ID + Client Secret (НЕ Authorization Key!):

```env
# GigaChat API - Client ID и Client Secret
GIGACHAT_CLIENT_ID=your-client-id-here
GIGACHAT_CLIENT_SECRET=your-client-secret-here
```

**⚠️ ВАЖНО:** 
- **Authorization Key** — это готовый ключ из личного кабинета (уже base64)
- **Client Secret** — это отдельный ключ (НЕ base64, НЕ Authorization Key!)
- Не путайте их! Если положите Authorization Key в `GIGACHAT_CLIENT_SECRET`, получите ошибку `Can't decode 'Authorization' header`

**Пример правильного `.env`:**
```env
# Вариант 1 (рекомендуется):
GIGACHAT_AUTH_KEY=01a07acf-911d-76cc-a7d4-36d5190004f5:MDfhMDdhY2Yt...

# Вариант 2:
GIGACHAT_CLIENT_ID=01a07acf-911d-76cc-a7d4-36d5190004f5
GIGACHAT_CLIENT_SECRET=MDfhMDdhY2Yt...
```

## 🔧 Как это работает

### Получение токена доступа

Backend автоматически получает токен доступа перед каждым вызовом GigaChat API:

```
POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth

Headers:
  Content-Type: application/x-www-form-urlencoded
  Accept: application/json
  RqUID: {UUIDv4}
  Authorization: Basic {base64(ClientID:ClientSecret)}

Body:
  scope=GIGACHAT_API_PERS

Response:
  {
    "access_token": "eyJhbGci...",
    "expires_at": 1739784663483
  }
```

### Использование токена

Токен используется для авторизации запросов к GigaChat API:

```
POST https://gigachat.devices.sberbank.ru/api/v1/chat/completions

Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body:
  {
    "model": "GigaChat",
    "messages": [...],
    "temperature": 0.7,
    "max_tokens": 2000
  }
```

## 🔄 Управление токенами

Backend автоматически управляет токенами:
- Токен кэшируется в памяти
- Обновляется за 120 секунд до истечения
- Используется single-flight refresh (один запрос на обновление)

## 🧪 Тестирование

### Проверка что credentials настроены

```bash
cd backend
python -c "from config import settings; print(f'Client ID: {settings.GIGACHAT_CLIENT_ID[:8]}...')"
```

Должно вывести первые 8 символов Client ID.

### Тестовый запрос к GigaChat

```bash
cd backend
python -c "
import asyncio
from llm_client import gigachat_client
from sqlalchemy.ext.asyncio import AsyncSession

async def test():
    try:
        token = await gigachat_client._get_token()
        print(f'✅ Token obtained: {token[:20]}...')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test())
"
```

Должно вывести: `✅ Token obtained: eyJhbGci...`

### Запуск урока

1. Перезапустите backend: `uvicorn main:app --reload`
2. Откройте http://localhost:3000
3. Начните урок
4. Проверьте логи backend - должны увидеть:
   ```
   ✅ Generated 3 exercises using GigaChat LLM
   ```

## ⚠️ Частые ошибки

### Ошибка: "credentials doesn't match db data"

**Причина:** Неправильные Client ID или Client Secret

**Решение:**
1. Проверьте что скопировали правильные credentials из личного кабинета
2. Убедитесь что нет лишних пробелов в `.env`
3. Перезапустите backend

### Ошибка: "GigaChat credentials not configured"

**Причина:** Не указаны credentials в `.env`

**Решение:**
1. Откройте `backend/.env`
2. Добавьте:
   ```env
   GIGACHAT_CLIENT_ID=your-client-id
   GIGACHAT_CLIENT_SECRET=your-client-secret
   ```
3. Перезапустите backend

### Ошибка: "401 Unauthorized"

**Причина:** Токен доступа истёк или недействителен

**Решение:**
- Backend автоматически обновляет токен
- Если ошибка повторяется, перезапустите backend

### Ошибка: "429 Too Many Requests"

**Причина:** Превышен лимит запросов к GigaChat API

**Решение:**
- Подождите минуту и попробуйте снова
- Для физических лиц лимит: 10 запросов в секунду на получение токена

### Ошибка: "503 Service Unavailable"

**Причина:** GigaChat API недоступен или credentials не настроены

**Решение:**
1. Проверьте что credentials настроены в `.env`
2. Проверьте что GigaChat API доступен: https://gigachat.devices.sberbank.ru
3. Если API недоступен, подождите и попробуйте позже
4. Frontend покажет сообщение: "Сервис временно недоступен. Попробуйте позже."

## 📊 Лимиты и тарифы

### Для физических лиц

- **Бесплатный лимит:** определённое количество токенов в месяц
- **Ограничения:** могут быть ограничения на количество запросов
- **Подробнее:** https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api

### Для ИП/Юридических лиц

- **Платные пакеты:** покупка токенов
- **Pay-as-you-go:** оплата по мере использования
- **Подробнее:** https://developers.sber.ru/docs/ru/gigachat/quickstart/legal-tokens-purchase

## 🔒 Безопасность

**Важно:**
- Никогда не коммитьте `.env` в git (уже добавлен в `.gitignore`)
- Не передавайте credentials третьим лицам
- Используйте разные credentials для development и production
- Регулярно ротируйте credentials

## 📚 Дополнительные ресурсы

- **Документация GigaChat API:** https://developers.sber.ru/docs/ru/gigachat/api
- **Личный кабинет Studio:** https://developers.sber.ru/studio
- **Быстрый старт для физических лиц:** https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api
- **Быстрый старт для ИП/ЮЛ:** https://developers.sber.ru/docs/ru/gigachat/quickstart/legal-using-api

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи backend
2. Проверьте что credentials настроены правильно
3. Проверьте что GigaChat API доступен
4. Обратитесь в поддержку Сбера: https://developers.sber.ru/
