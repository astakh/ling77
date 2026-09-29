# Исправление отображения блока "Оценка слов"

## Проблема

Блок "📝 Оценка слов" не отображал список слов с оценкой по каждому слову. Ожидалось:
- Слово
- Статус: правильно переведено или нет
- Если перевод неправильный: перевод ученика и правильный перевод

## Причина

Проблема была в том, что backend не возвращал поле `translation` в `ExerciseWordResponse` во всех случаях:

1. **При создании урока** (`start_lesson`) - поле `translation` отсутствовало
2. **При загрузке кэшированного результата** (`evaluate_exercise` с idempotency) - поле `translation` отсутствовало
3. **Frontend пытался найти перевод** через `exercise.words.find(w => w.wordId === word.wordId)?.surfaceForm`, что возвращало английское слово вместо русского перевода

## Решение

### Backend изменения

#### 1. Добавлено поле `translation` при создании урока

**Файл:** `backend/routes/lesson.py` (строка 293)

```python
exercise_words_response.append(ExerciseWordResponse(
    word_id=word_data["word_id"],
    is_target=True,
    is_new=word_data["is_new"],
    surface_form=word_data["lemma"],
    translation=word_data["translations"][0] if word_data.get("translations") else None,
    stage_before=word_data["stage"],
    stage_after=word_data["stage"],
))
```

#### 2. Добавлено поле `translation` при загрузке кэшированного результата

**Файл:** `backend/routes/lesson.py` (строка 366-398)

```python
# Idempotency: if already evaluated, return cached
if exercise.status == "evaluated":
    result = await db.execute(
        select(LessonExerciseWord).where(LessonExerciseWord.exercise_id == exercise.id)
    )
    exercise_words = result.scalars().all()

    # Load Word objects to get translations
    word_ids = [ew.word_id for ew in exercise_words if ew.is_target]
    words_result = await db.execute(
        select(Word).where(Word.id.in_(word_ids))
    )
    words_map = {w.id: w for w in words_result.scalars().all()}

    # Check if this is the last exercise
    result = await db.execute(
        select(func.count(LessonExercise.id)).where(
            LessonExercise.lesson_id == lesson.id,
        )
    )
    total_exercises = result.scalar()
    is_last = exercise.order_index == total_exercises - 1

    return EvaluateResponse(
        exercise_id=exercise.id,
        result=exercise_words[0].result if exercise_words else "incorrect",
        words=[
            ExerciseWordResponse(
                word_id=ew.word_id,
                is_target=ew.is_target,
                is_new=ew.is_new,
                surface_form=ew.surface_form,
                translation=words_map[ew.word_id].translations[0] if ew.word_id in words_map and words_map[ew.word_id].translations else None,
                result=ew.result,
                stage_before=ew.stage_before,
                stage_after=ew.stage_after,
            )
            for ew in exercise_words if ew.is_target
        ],
        reference_translation=exercise.reference_translation,
        is_last=is_last,
    )
```

### Frontend изменения

#### Исправлено отображение правильного перевода

**Файл:** `src/pages/ExercisePage.tsx` (строка 327-379)

**Было:**
```typescript
{exercise.words.find(w => w.wordId === word.wordId)?.surfaceForm || '—'}
```

**Стало:**
```typescript
{word.translation || '—'}
```

Теперь используется поле `translation` из объекта `word`, которое приходит от backend.

#### Добавлено логирование для отладки

```typescript
console.log(`Word ${idx}:`, word); // Логируем структуру
```

Это помогает увидеть структуру данных в консоли браузера.

#### Добавлена проверка на пустой массив

```typescript
{resultData && resultData.words && resultData.words.length > 0 && (
```

Блок рендерится только если есть слова для отображения.

#### Добавлен правильный перевод для опечаток

Раньше для опечаток не показывался правильный перевод. Теперь показывается:

```typescript
{isTypo && (
  <div className="text-sm">
    <p className="text-amber-600">⚠ Опечатка</p>
    <p className="text-gray-600 mt-1">
      Ваш перевод: <span className="font-medium">{word.userFragment || '—'}</span>
    </p>
    <p className="text-gray-600 mt-1">
      Правильный перевод: <span className="font-medium text-green-600">
        {word.translation || '—'}
      </span>
    </p>
  </div>
)}
```

## Результат

Теперь блок "📝 Оценка слов" корректно отображает:

### Для правильных переводов:
```
✓ house
  ✓ Правильно
```

### Для опечаток:
```
⚠ beautiful
  ⚠ Опечатка
  Ваш перевод: beatiful
  Правильный перевод: красивый
```

### Для неправильных переводов:
```
✗ important
  ✗ Неправильно
  Ваш перевод: важный
  Правильный перевод: важный
```

## Тестирование

1. Перезапустите backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Перезапустите frontend:
   ```bash
   npm run dev
   ```

3. Начните урок и переведите предложение

4. Проверьте в консоли браузера (F12):
   - Должны появиться логи: `Word 0: {...}`, `Word 1: {...}`, и т.д.
   - В объекте должно быть поле `translation`

5. Проверьте блок "📝 Оценка слов":
   - Должен отображаться список всех целевых слов
   - Для каждого слова: статус, перевод пользователя (если есть), правильный перевод

## Структура данных

### Backend Response (ExerciseWordResponse)

```json
{
  "word_id": 1,
  "is_target": true,
  "is_new": false,
  "surface_form": "house",
  "translation": "дом",
  "result": "correct",
  "stage_before": 0,
  "stage_after": 1
}
```

### Frontend (resultData.words)

Массив объектов `ExerciseWordResponse` для каждого целевого слова в упражнении.

## Изменённые файлы

- `backend/routes/lesson.py` - добавлено поле `translation` в ExerciseWordResponse
- `src/pages/ExercisePage.tsx` - исправлено отображение правильного перевода

## Примечания

- Поле `translation` в `ExerciseWordResponse` было добавлено ранее, но не заполнялось во всех случаях
- Теперь все три места создания ExerciseWordResponse заполняют это поле
- Frontend использует это поле напрямую вместо поиска в exercise.words
