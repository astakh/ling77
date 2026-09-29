# 🔧 Fallback для LLM (GigaChat)

## 📋 Проблема

При запуске урока backend пытается вызвать GigaChat API для генерации упражнений и оценки переводов. Если:
- Не настроены credentials в `.env`
- API недоступен
- Неправильный формат запроса

Backend возвращает ошибку **503 Service Unavailable**.

## ✅ Решение

Реализован **fallback механизм** - если GigaChat недоступен, backend автоматически использует локальные генераторы без LLM.

### Что изменилось

**Файл:** `backend/exercise_generator.py` (новый)
- `generate_exercises_fallback()` - генерация упражнений без LLM
- `_fallback_evaluate_translation()` - оценка переводов без LLM
- `_similar_words()` - проверка похожести слов для определения опечаток

**Файл:** `backend/routes/lesson.py`
- `POST /lesson/start` - теперь использует fallback при ошибке LLM
- `POST /lesson/evaluate` - теперь использует fallback при ошибке LLM

## 🔄 Как это работает

### Генерация упражнений (POST /lesson/start)

```python
try:
    # Пытаемся использовать GigaChat
    llm_results = await gigachat_client.generate_exercises(...)
    logger.info("✅ Generated exercises using GigaChat LLM")
except Exception as e:
    # Если не получилось - используем fallback
    logger.warning(f"⚠️ LLM generation failed: {e}. Using fallback generator.")
    llm_results = generate_exercises_fallback(clusters, profile.level)
    logger.info("✅ Generated exercises using fallback (no LLM)")
```

### Оценка переводов (POST /lesson/evaluate)

```python
try:
    # Пытаемся использовать GigaChat
    llm_result = await gigachat_client.evaluate_translation(...)
    logger.info("✅ Translation evaluated using GigaChat LLM")
except Exception as e:
    # Если не получилось - используем fallback
    logger.warning(f"⚠️ LLM evaluation failed: {e}. Using fallback evaluation.")
    overall_result, evaluations = _fallback_evaluate_translation(...)
    logger.info("✅ Translation evaluated using fallback (no LLM)")
```

## 📝 Fallback генератор упражнений

### Как работает

Использует предопределённые шаблоны предложений для разных частей речи:

```python
SENTENCE_TEMPLATES = {
    "noun": [
        "The {word} is very important.",
        "I see a {word} every day.",
        ...
    ],
    "verb": [
        "I {word} every morning.",
        "She likes to {word} in the park.",
        ...
    ],
    ...
}
```

### Пример

**Входные данные:**
- Слово: `house` (noun)
- Перевод: `дом`

**Сгенерированное упражнение:**
```json
{
  "sentence": "The house is very important.",
  "reference_translation": "Дом очень важен."
}
```

### Ограничения

- Шаблоны простые и предсказуемые
- Не учитывает контекст и уровень сложности
- Может генерировать повторяющиеся предложения

## 📝 Fallback оценка переводов

### Как работает

Использует простое сопоставление ключевых слов:

1. **Точное совпадение** - если перевод слова есть в пользовательском вводе
2. **Проверка опечаток** - если слова похожи (70%+ символов совпадают)
3. **Результат**: `correct`, `typo`, или `incorrect`

### Пример

**Целевое слово:** `house` → `дом`

**Пользовательский перевод:** `Этот дом очень красивый`

**Оценка:**
```json
{
  "word_lemma": "house",
  "result": "correct",
  "user_fragment": "дом"
}
```

### Ограничения

- Не понимает контекст и грамматику
- Может пропустить семантические ошибки
- Простая проверка опечаток (может дать ложные срабатывания)

## 🚀 Как использовать

### Вариант 1: Без GigaChat (по умолчанию)

Если credentials не настроены, fallback используется автоматически.

**`.env`:**
```env
# GigaChat credentials не указаны
# GIGACHAT_CLIENT_ID=
# GIGACHAT_CLIENT_SECRET=
```

**Результат:** Backend использует fallback генераторы.

### Вариант 2: С GigaChat (если есть credentials)

**`.env`:**
```env
GIGACHAT_CLIENT_ID=your-client-id
GIGACHAT_CLIENT_SECRET=your-client-secret
```

**Результат:** Backend пытается использовать GigaChat, при ошибке переключается на fallback.

## 📊 Логи

### При успешном использовании GigaChat:
```
✅ Generated 3 exercises using GigaChat LLM
✅ Translation evaluated using GigaChat LLM
```

### При использовании fallback:
```
⚠️ LLM generation failed: Client error '400 Bad Request'. Using fallback generator.
✅ Generated 3 exercises using fallback (no LLM)

⚠️ LLM evaluation failed: Connection timeout. Using fallback evaluation.
✅ Translation evaluated using fallback (no LLM)
```

## 🧪 Тестирование

### Тест 1: Запуск урока без GigaChat

1. Убедитесь что credentials не настроены в `.env`
2. Перезапустите backend: `uvicorn main:app --reload`
3. Начните урок через frontend
4. Проверьте логи backend - должны увидеть "Using fallback generator"
5. Упражнение должно успешно создаться

### Тест 2: Оценка перевода без GigaChat

1. Пройдите до упражнения
2. Введите перевод (например, "дом")
3. Нажмите "Проверить"
4. Проверьте логи backend - должны увидеть "Using fallback evaluation"
5. Результат должен быть `correct`, `typo`, или `incorrect`

### Тест 3: Проверка fallback оценки

**Правильный перевод:**
- Пользователь: "Этот дом очень красивый"
- Целевое слово: `house` → `дом`
- Ожидается: `correct`

**Опечатка:**
- Пользователь: "Этот дм очень красивый"
- Целевое слово: `house` → `дом`
- Ожидается: `typo`

**Неправильный перевод:**
- Пользователь: "Эта машина быстрая"
- Целевое слово: `house` → `дом`
- Ожидается: `incorrect`

## 🔧 Улучшение fallback генератора

Если нужно более качественное генерирование упражнений без LLM, можно:

1. **Добавить больше шаблонов** в `exercise_generator.py`
2. **Использовать предопределённые предложения** из файла `src/data/sentences.ts`
3. **Загрузить предложения из БД** (таблица `sentence_templates`)
4. **Использовать другой LLM API** (OpenAI, Anthropic, etc.)

### Пример: Загрузка предложений из БД

```python
# Создать таблицу sentence_templates
CREATE TABLE sentence_templates (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    sentence TEXT NOT NULL,
    translation TEXT NOT NULL,
    level VARCHAR(2) NOT NULL
);

# Использовать в fallback генераторе
async def get_template_for_word(db, word_id):
    result = await db.execute(
        select(SentenceTemplate).where(
            SentenceTemplate.word_id == word_id
        ).limit(1)
    )
    return result.scalar_one_or_none()
```

## 📚 Связанные файлы

- `backend/exercise_generator.py` - fallback генераторы
- `backend/routes/lesson.py` - endpoints для уроков
- `backend/llm_client.py` - GigaChat клиент
- `backend/.env` - конфигурация credentials

## 🎯 Итог

✅ Backend работает **без GigaChat** (использует fallback)  
✅ Backend работает **с GigaChat** (если настроены credentials)  
✅ Автоматическое переключение при ошибках LLM  
✅ Логи показывают какой режим используется  
✅ Можно улучшить fallback генераторы без изменения основной логики

**Рекомендация:** Для production используйте GigaChat или другой LLM для лучшего качества. Fallback подходит для разработки и тестирования.
