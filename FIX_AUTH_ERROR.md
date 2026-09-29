# 🚨 Исправление ошибки "Can't decode 'Authorization' header"

## ❌ Проблема

В логах backend видна ошибка:
```
Response body: {"code":4,"message":"Can't decode 'Authorization' header"}
```

## 🔍 Причина

В поле `GIGACHAT_CLIENT_SECRET` в файле `.env` указан **Authorization Key** (уже закодированный в base64), а не **Client Secret**.

Когда backend делает `base64(ClientID:ClientSecret)`, происходит **двойное кодирование**, и GigaChat не может декодировать заголовок.

## ✅ Решение

### Вариант 1 (рекомендуется): Использовать Authorization Key

Откройте `backend/.env` и замените содержимое на:

```env
# GigaChat - Authorization Key из личного кабинета
GIGACHAT_AUTH_KEY=ваш-authorization-key-из-studio
```

**Удалите** строки `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET` если они есть.

### Вариант 2: Использовать Client ID + Client Secret

Если хотите использовать Client ID и Client Secret, убедитесь что в `.env`:

```env
# Client ID из личного кабинета (UUID формат)
GIGACHAT_CLIENT_ID=01a07acf-911d-76cc-a7d4-36d5190004f5

# Client Secret из личного кабинета (НЕ Authorization Key!)
GIGACHAT_CLIENT_SECRET=MDfhMDdhY2YtOTExZC03NmNjLWE3ZDQtMzZkNTE5MDAwNGY1
```

**⚠️ ВАЖНО:** 
- `GIGACHAT_CLIENT_SECRET` должен быть **Client Secret** из личного кабинета
- **НЕ** Authorization Key (который уже base64)
- **НЕ** строка вида `Basic dGVzdDp0ZXN0`

## 📋 Как получить правильные credentials

1. Перейдите на https://developers.sber.ru/studio
2. Откройте ваш проект GigaChat API
3. Найдите раздел "Credentials" или "Авторизация"
4. Вы увидите:
   - **Client ID** (UUID формат: `01a07acf-911d-76cc-...`)
   - **Client Secret** (длинная строка)
   - **Authorization Key** (готовый base64 ключ)

### Что куда класть:

| Поле в `.env` | Что туда класть |
|---------------|-----------------|
| `GIGACHAT_AUTH_KEY` | Authorization Key из личного кабинета |
| `GIGACHAT_CLIENT_ID` | Client ID из личного кабинета |
| `GIGACHAT_CLIENT_SECRET` | Client Secret из личного кабинета (НЕ Authorization Key!) |

## 🔄 После исправления

1. Сохраните `backend/.env`
2. Перезапустите backend:
   ```bash
   uvicorn main:app --reload
   ```
3. Попробуйте начать урок снова
4. В логах должно быть:
   ```
   ✅ GigaChat token obtained successfully
   ✅ Generated 3 exercises using GigaChat LLM
   ```

## 🧪 Проверка

Выполните скрипт проверки:
```bash
cd backend
python scripts/check_gigachat.py
```

Он покажет какие credentials настроены и правильно ли они указаны.

## 📚 Дополнительная информация

- [Полная настройка GigaChat](./docs/GIGACHAT_SETUP.md)
- [Обработка ошибок LLM](./docs/LLM_ERROR_HANDLING.md)
- [Документация GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-token)
