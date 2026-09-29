# 🔑 Настройка GigaChat API - ПОШАГОВАЯ ИНСТРУКЦИЯ

## ⚠️ ВАЖНО: Разница между Authorization Key и Client Secret

В личном кабинете Studio вы видите **ТРИ** значения:

| Поле | Что это | Как использовать |
|------|---------|------------------|
| **Client ID** | UUID (например: `01a07acf-911d-76cc-a7d4-36d5190004f5`) | Используется с Client Secret |
| **Client Secret** | Секретный ключ (строка) | Используется с Client ID |
| **Authorization Key** | Готовый ключ вида `UUID:base64string` | ✅ **ИСПОЛЬЗУЙТЕ ЭТО!** |

### ❌ Частая ошибка

**НЕ ПУТАЙТЕ** Client Secret и Authorization Key!

- **Authorization Key** = `01a07acf-911d-76cc-...:MDfhMDdhY2Yt...` (длинная строка с `:`)
- **Client Secret** = короткая строка без `:`

Если вы положите Authorization Key в `GIGACHAT_CLIENT_SECRET`, получите ошибку:
```
Can't decode 'Authorization' header
```

## 🚀 Правильная настройка (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Получите Authorization Key

1. Перейдите на https://developers.sber.ru/studio
2. Откройте ваш проект GigaChat API
3. Найдите раздел **"Credentials"** или **"Авторизация"**
4. Скопируйте **Authorization Key** (длинная строка вида `UUID:base64string`)

### Шаг 2: Откройте backend/.env

```bash
# В VSCode или любом редакторе
code backend/.env
```

### Шаг 3: Добавьте Authorization Key

```env
# GigaChat API - Authorization Key из личного кабинета
GIGACHAT_AUTH_KEY=01a07acf-911d-76cc-a7d4-36d5190004f5:MDfhMDdhY2YtOTExZC03NmNjLWE3ZDQtMzZkNTE5MDAwNGY1...
```

**ВАЖНО:** 
- Удалите или закомментируйте `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET`
- Используйте **ТОЛЬКО** `GIGACHAT_AUTH_KEY`

### Шаг 4: Сохраните и перезапустите backend

```bash
# В терминале backend
# Нажмите Ctrl+C чтобы остановить
uvicorn main:app --reload
```

### Шаг 5: Проверьте логи

При запуске урока в логах должно быть:

```
🔑 Using GIGACHAT_AUTH_KEY (Authorization Key from Studio)
   Auth Key preview: 01a07acf-911d-76cc-a7d4...
   Auth Key length: 150 chars

🔑 Requesting GigaChat access token...
   URL: https://ngw.devices.sberbank.ru:9443/api/v2/oauth
   RqUID: 12345678-1234-1234-1234-123456789012
   Source: GIGACHAT_AUTH_KEY
   Scope: GIGACHAT_API_PERS

📥 GigaChat OAuth response: 200

✅ GigaChat access token obtained successfully!
   Token preview: eyJhbGci...
   Token expires at: 1739784663483
   Token valid for 30 minutes

✅ Generated 3 exercises using GigaChat LLM
```

## 🔄 Как работает обновление токена

Согласно документации GigaChat:
- Токен доступа действителен **30 минут**
- Backend автоматически обновляет токен за **120 секунд** до истечения
- Используется **single-flight refresh** (один запрос на обновление)

Вам **НЕ НУЖНО** вручную обновлять токен - backend делает это автоматически.

## 🧪 Проверка настройки

Выполните скрипт проверки:

```bash
cd backend
python scripts/check_gigachat.py
```

Он покажет:
- ✅ Какие credentials настроены
- ✅ Правильный ли формат
- ✅ Что делать если есть ошибки

## ❌ Если всё ещё ошибка 400

### Ошибка: "Can't decode 'Authorization' header"

**Причина:** Неправильный формат Authorization Key

**Решение:**
1. Убедитесь что используете **Authorization Key**, а не Client Secret
2. Проверьте что в `.env` только `GIGACHAT_AUTH_KEY` (без `GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET`)
3. Убедитесь что нет лишних пробелов в `.env`
4. Перезапустите backend

### Ошибка: "credentials doesn't match db data"

**Причина:** Неправильные credentials

**Решение:**
1. Скопируйте Authorization Key заново из личного кабинета
2. Убедитесь что скопировали полную строку (не обрезали)
3. Перезапустите backend

### Ошибка: "GigaChat credentials not configured"

**Причина:** Не указаны credentials в `.env`

**Решение:**
1. Откройте `backend/.env`
2. Добавьте `GIGACHAT_AUTH_KEY=...`
3. Перезапустите backend

## 📚 Документация GigaChat

- **Получение токена:** https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-token
- **Быстрый старт:** https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-using-api
- **Личный кабинет:** https://developers.sber.ru/studio

## 💡 Подсказка

Если вы не уверены что использовать - используйте **Authorization Key** (`GIGACHAT_AUTH_KEY`). Это самый простой и надёжный способ.

Authorization Key - это готовый ключ из личного кабинета, который уже содержит закодированные Client ID и Client Secret. Вам не нужно ничего кодировать самостоятельно.
