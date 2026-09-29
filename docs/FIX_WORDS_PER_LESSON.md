# Исправление алгоритма выбора слов для урока

## Проблема

Алгоритм выбора слов для урока использовал захардкоженные значения вместо настроек пользователя:
- Захардкоженное количество слов: `8`
- Захардкоженный лимит due слов: `5`

Это игнорировало настройки пользователя `words_per_lesson` из профиля.

## Решение

Изменен файл `backend/routes/lesson.py` в функции `select_words_for_lesson()`:

### 1. Динамический лимит due слов

**Было:**
```python
due_words = due_words[:5]  # max 5 due words
```

**Стало:**
```python
# Max 60% of words_per_lesson for due words (but at least 3)
max_due_words = max(int(profile.words_per_lesson * 0.6), 3)
due_words = due_words[:max_due_words]
```

### 2. Динамическое количество новых слов

**Было:**
```python
remaining = max(8 - len(due_words), 3)
new_words = new_words[:remaining]
```

**Стало:**
```python
# Fill remaining slots with new words to reach words_per_lesson
remaining = max(profile.words_per_lesson - len(due_words), 0)
new_words = new_words[:remaining]
```

## Проверка требований

### ✅ 1. Количество слов из профиля пользователя

Теперь алгоритм использует `profile.words_per_lesson`:
- Общее количество слов в уроке = `profile.words_per_lesson`
- Due слова (повторение) = до 60% от `words_per_lesson` (но не менее 3)
- Новые слова = остаток до `words_per_lesson`

**Примеры:**
- `words_per_lesson = 10` → due: до 6 слов, new: 4 слова
- `words_per_lesson = 8` → due: до 5 слов, new: 3 слова
- `words_per_lesson = 5` → due: до 3 слов, new: 2 слова

### ✅ 2. Фильтрация по выбранному словарю

Алгоритм уже правильно фильтрует слова по `profile.dictionary_id`:

```python
result = await db.execute(
    select(Word)
    .join(DictionaryWord, DictionaryWord.word_id == Word.id)
    .where(
        DictionaryWord.dictionary_id == profile.dictionary_id,
        Word.level.in_(allowed_levels),
    )
)
```

### ✅ 3. Фильтрация по уровню пользователя

Алгоритм уже правильно фильтрует слова по `profile.level`:

```python
level_order = {"A1": 1, "A2": 2, "B1": 3, "B2": 4}
allowed_levels = [
    lvl for lvl, order in level_order.items()
    if order <= level_order.get(profile.level, 4)
]
```

Пользователь с уровнем B1 видит слова уровней A1, A2, B1.

## Тестирование

### Проверка в базе данных

```sql
-- Проверить настройки пользователя
SELECT user_id, level, dictionary_id, words_per_lesson, daily_lesson_limit
FROM learning_profiles
WHERE user_id = 2;

-- Проверить слова в уроке
SELECT COUNT(*) as total_words,
       SUM(CASE WHEN is_new THEN 1 ELSE 0 END) as new_words,
       SUM(CASE WHEN NOT is_new THEN 1 ELSE 0 END) as due_words
FROM lesson_exercise_words
WHERE exercise_id IN (
    SELECT id FROM lesson_exercises
    WHERE lesson_id = (
        SELECT id FROM lessons
        WHERE learning_profile_id = (
            SELECT id FROM learning_profiles WHERE user_id = 2
        )
        ORDER BY lesson_number DESC
        LIMIT 1
    )
);
```

### Проверка через API

1. Измените настройки пользователя через `/settings`:
   - Установите `words_per_lesson = 10`

2. Начните новый урок через `/lesson/start`

3. Проверьте количество слов в ответе:
   - Должно быть 10 слов (или меньше, если нет доступных слов)

## Логика алгоритма

```
1. Получить due слова (готовые к повторению)
   - Из user_words пользователя
   - Где stage < 6 и due_lesson_number <= current_lesson
   - Отсортировать по детерминированному хешу
   - Взять до 60% от words_per_lesson (минимум 3)

2. Получить новые слова
   - Из выбранного словаря (dictionary_id)
   - Уровень слова <= уровень пользователя
   - Слова, которых еще нет у пользователя
   - Отсортировать по детерминированному хешу
   - Взять остаток до words_per_lesson

3. Объединить due_words + new_words
   - Общее количество <= words_per_lesson

4. Сгруппировать в кластеры по 2-3 слова
   - Для генерации упражнений через LLM
```

## Измененные файлы

- `backend/routes/lesson.py` - функция `select_words_for_lesson()`

## Связанные документы

- `docs/DICTIONARY_ARCHITECTURE.md` - архитектура словарей
- `docs/CREATE_UNIVERSAL_DICTIONARY.md` - универсальный словарь
- `SETTINGS_QUICKSTART.md` - настройки пользователя
