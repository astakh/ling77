# Исправление отображения оценки слов и new_suggested_words

## Проблема 1: new_suggested_words не содержит переводы

**Было:**
```json
{
  "new_suggested_words": ["word1", "word2"]
}
```

**Стало:**
```json
{
  "new_suggested_words": [
    {
      "word": "consider",
      "translation": "рассматривать"
    }
  ]
}
```

## Проблема 2: Блок оценки слов отображал только одно слово

**Причина:** Frontend использовал `word.userFragment` (camelCase), но backend возвращал `user_fragment` (snake_case). Также отсутствовало поле `translation` в некоторых случаях.

## Изменения

### 1. Обновлен промпт для LLM

**Файл:** `backend/prompts/evaluate_translation.txt`

Изменен формат `new_suggested_words` с массива строк на массив объектов:

```
"new_suggested_words": [
  {
    "word": "английское слово",
    "translation": "правильный перевод на русский"
  }
]
```

### 2. Обновлена валидация ответа LLM

**Файл:** `backend/llm_client.py`

```python
# Validate new_suggested_words - should be list of objects with word and translation
for i, word_obj in enumerate(result["new_suggested_words"]):
    if not isinstance(word_obj, dict):
        logger.warning(f"   ❌ new_suggested_words[{i}] is not an object: {type(word_obj)}")
        return False
    if "word" not in word_obj or "translation" not in word_obj:
        logger.warning(f"   ❌ new_suggested_words[{i}] missing required fields")
        return False
```

### 3. Упрощена обработка new_suggested_words в backend

**Файл:** `backend/routes/lesson.py`

Убран лишний поиск слов в базе данных. Теперь переводы берутся напрямую из ответа LLM:

```python
new_suggested_words = llm_result.get("new_suggested_words", [])
```

### 4. Добавлено поле user_fragment в схему

**Файл:** `backend/schemas.py`

```python
class ExerciseWordResponse(BaseModel):
    word_id: int
    is_target: bool
    is_new: bool
    surface_form: str
    translation: Optional[str] = None
    result: Optional[str] = None
    user_fragment: Optional[str] = None  # Добавлено
    stage_before: int
    stage_after: int
```

### 5. Добавлено логирование в backend

**Файл:** `backend/routes/lesson.py`

```python
logger.info(f"📝 Exercise words response: {len(exercise_words_response)} words")
for i, ewr in enumerate(exercise_words_response):
    logger.info(f"   Word {i}: {ewr.surface_form} - {ewr.result} - {ewr.translation}")
```

### 6. Исправлен маппинг полей на frontend

**Файл:** `src/pages/ExercisePage.tsx`

Добавлена поддержка обоих форматов (snake_case и camelCase):

```typescript
const userFragment = word.user_fragment || word.userFragment;
const surfaceForm = word.surface_form || word.surfaceForm;
```

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

### 3. Начните урок и переведите предложение

### 4. Проверьте логи backend

В терминале backend должны появиться логи:

```
📝 Exercise words response: 2 words
   Word 0: consider - incorrect - рассматривать
   Word 1: bridge - correct - мост
```

### 5. Проверьте консоль браузера

В консоли браузера (F12) должны появиться логи:

```
Word 0: {word_id: 1, surface_form: "consider", translation: "рассматривать", result: "incorrect", user_fragment: "важный"}
Word 1: {word_id: 2, surface_form: "bridge", translation: "мост", result: "correct", user_fragment: "мост"}
```

### 6. Проверьте отображение

Блок "📝 Оценка слов" должен отображать **все** целевые слова:

```
📝 ОЦЕНКА СЛОВ

✗ consider
  ✗ Неправильно
  Ваш перевод: важный
  Правильный перевод: рассматривать

✓ bridge
  ✓ Правильно
```

Блок "💡 Добавить в словарь" должен отображать слова с переводами:

```
💡 ДОБАВИТЬ В СЛОВАРЬ

☐ important — важный
☐ software — программа
```

## Структура данных

### Backend Response

```json
{
  "exercise_id": 1,
  "result": "incorrect",
  "words": [
    {
      "word_id": 1,
      "is_target": true,
      "is_new": false,
      "surface_form": "consider",
      "translation": "рассматривать",
      "result": "incorrect",
      "user_fragment": "важный",
      "stage_before": 0,
      "stage_after": 0
    },
    {
      "word_id": 2,
      "is_target": true,
      "is_new": false,
      "surface_form": "bridge",
      "translation": "мост",
      "result": "correct",
      "user_fragment": "мост",
      "stage_before": 0,
      "stage_after": 1
    }
  ],
  "reference_translation": "Нам нужно рассмотреть мост",
  "is_last": false,
  "new_suggested_words": [
    {
      "word": "important",
      "translation": "важный"
    },
    {
      "word": "software",
      "translation": "программа"
    }
  ]
}
```

### Frontend Processing

```typescript
// Маппинг полей
const userFragment = word.user_fragment || word.userFragment;
const surfaceForm = word.surface_form || word.surfaceForm;

// Отображение
<p>{surfaceForm}</p>
<p>Ваш перевод: {userFragment}</p>
<p>Правильный перевод: {word.translation}</p>
```

## Изменённые файлы

- `backend/prompts/evaluate_translation.txt` - обновлен формат new_suggested_words
- `backend/llm_client.py` - обновлена валидация
- `backend/routes/lesson.py` - упрощена обработка, добавлено логирование
- `backend/schemas.py` - добавлено поле user_fragment
- `src/pages/ExercisePage.tsx` - исправлен маппинг полей

## Примечания

1. **Совместимость:** Frontend поддерживает оба формата полей (snake_case и camelCase) для обратной совместимости
2. **Логирование:** Добавлено подробное логирование на backend и frontend для отладки
3. **Валидация:** LLM теперь возвращает объекты с переводами, что упрощает обработку

## Тестирование

1. Переведите предложение с ошибками
2. Проверьте что все целевые слова отображаются в блоке оценки
3. Проверьте что новые слова отображаются с переводами
4. Проверьте логи backend и консоли браузера
