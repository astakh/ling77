# Новый алгоритм выбора слов для урока

## Дата обновления
2026-09-29

## Изменения в алгоритме

### Старый алгоритм
- Захардкоженное количество слов: 8
- Due слова: до 60% от words_per_lesson (минимум 3)
- Новые слова: остаток до 8 слов
- Сортировка due слов: по детерминированному хешу

### Новый алгоритм
- Динамическое количество слов: `words_per_lesson` из профиля пользователя
- **Гарантия минимум 1 нового слова**
- Если не хватает слов до `words_per_lesson`, добавляются новые слова
- Если due слов слишком много, берутся **самые перезревшие** (most overdue)
- Сортировка due слов: по перезрелости (убывание), затем по хешу

## Логика работы

### Шаг 1: Сбор due слов с расчётом перезрелости
```python
overdue = profile.last_lesson_number - (uw.due_lesson_number or 0)
```
Чем больше значение `overdue`, тем дольше слово ждёт повторения.

### Шаг 2: Сортировка due слов
```python
due_words.sort(key=lambda x: (-x["overdue"], x["hash"]))
```
Сначала по перезрелости (убывание), затем по хешу для детерминированности.

### Шаг 3: Сбор новых слов
Новые слова сортируются по детерминированному хешу.

### Шаг 4: Формирование итогового набора
```python
target_total = profile.words_per_lesson

# 1. Гарантируем минимум 1 новое слово
if new_words:
    selected_new_words.append(new_words[0])

# 2. Берём due слова (самые перезревшие)
max_due = target_total - len(selected_new_words)
selected_due_words = due_words[:max_due]

# 3. Заполняем остаток новыми словами
remaining = target_total - len(selected_due_words) - len(selected_new_words)
if remaining > 0 and new_words:
    selected_new_words.extend(new_words[:remaining])
```

## Примеры

### Пример 1: words_per_lesson = 10, 15 due слов, 20 new слов
```
1. Берём 1 новое слово (гарантия)
2. Берём 9 due слов (самые перезревшие из 15)
3. Итого: 9 due + 1 new = 10 слов
```

### Пример 2: words_per_lesson = 10, 3 due слова, 20 new слов
```
1. Берём 1 новое слово (гарантия)
2. Берём 3 due слова (все доступные)
3. Берём ещё 6 новых слов (10 - 3 - 1 = 6)
4. Итого: 3 due + 7 new = 10 слов
```

### Пример 3: words_per_lesson = 10, 0 due слов, 20 new слов
```
1. Берём 1 новое слово (гарантия)
2. Нет due слов
3. Берём ещё 9 новых слов (10 - 0 - 1 = 9)
4. Итого: 0 due + 10 new = 10 слов
```

### Пример 4: words_per_lesson = 10, 20 due слов, 0 new слов
```
1. Нет новых слов для гарантии
2. Берём 10 due слов (самые перезревшие из 20)
3. Итого: 10 due + 0 new = 10 слов
```

### Пример 5: words_per_lesson = 10, 2 due слова, 2 new слова
```
1. Берём 1 новое слово (гарантия)
2. Берём 2 due слова
3. Берём ещё 1 новое слово (10 - 2 - 1 = 7, но доступно только 1)
4. Итого: 2 due + 2 new = 4 слова (меньше target, т.к. не хватает слов)
```

## Преимущества нового алгоритма

### 1. Гибкость
- Адаптируется к количеству доступных слов
- Гарантирует разнообразие (минимум 1 новое слово)

### 2. Приоритет перезревших слов
- Слова, которые давно ждут повторения, получают приоритет
- Улучшает эффективность интервального повторения

### 3. Динамическое количество слов
- Использует `words_per_lesson` из настроек пользователя
- Пользователь может настроить количество слов в уроке

### 4. Детерминированность
- Сохраняется детерминированный хеш для воспроизводимости
- При одинаковых условиях выбираются одинаковые слова

## Изменения в коде

### Файл: `backend/routes/lesson.py`

#### Добавлено поле `overdue` в due_words
```python
overdue = profile.last_lesson_number - (uw.due_lesson_number or 0)
due_words.append({
    ...
    "overdue": overdue,
    ...
})
```

#### Изменена сортировка due_words
```python
# Было:
due_words.sort(key=lambda x: x["hash"])

# Стало:
due_words.sort(key=lambda x: (-x["overdue"], x["hash"]))
```

#### Новый алгоритм выбора слов
```python
# Гарантируем минимум 1 новое слово
if new_words:
    selected_new_words.append(new_words[0])
    new_words = new_words[1:]

# Берём due слова (самые перезревшие)
max_due = target_total - len(selected_new_words)
selected_due_words = due_words[:max_due]

# Заполняем остаток новыми словами
remaining = target_total - len(selected_due_words) - len(selected_new_words)
if remaining > 0 and new_words:
    selected_new_words.extend(new_words[:remaining])
```

## Тестирование

### Проверка в базе данных
```sql
-- Проверить настройки пользователя
SELECT user_id, words_per_lesson
FROM learning_profiles
WHERE user_id = 2;

-- Проверить слова в последнем уроке
SELECT 
    COUNT(*) as total_words,
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

### Проверка через логи
В логах backend должно быть:
```
📝 Exercise words response: 10 words
   Word 0: consider - correct - рассматривать - user_fragment='...'
   Word 1: algorithm - correct - алгоритм - user_fragment='...'
   ...
```

## Обратная совместимость

### Что изменилось
- Количество слов в уроке теперь динамическое
- Приоритет due слов изменился (по перезрелости, а не по хешу)
- Гарантируется минимум 1 новое слово

### Что не изменилось
- Фильтрация по словарю (`dictionary_id`)
- Фильтрация по уровню (`level`)
- Детерминированный хеш для новых слов
- Структура данных (due_words, new_words)

### Миграция данных
Не требуется. Алгоритм работает с существующими данными.

## Связанные документы

- `docs/FIX_WORDS_PER_LESSON.md` - предыдущее исправление
- `docs/DICTIONARY_ARCHITECTURE.md` - архитектура словарей
- `WORDS_PER_LESSON_FIX.md` - краткая инструкция

## Будущие улучшения

### 1. Взвешенный выбор due слов
Можно учитывать не только перезрелость, но и:
- Сложность слова (stage)
- Частоту ошибок пользователя
- Время суток (утром легче учить новые слова)

### 2. Адаптивное количество новых слов
Можно динамически менять соотношение due/new в зависимости от:
- Успешности пользователя на прошлом уроке
- Количества доступных due слов
- Уровня пользователя

### 3. Приоритизация новых слов
Можно сортировать новые слова по:
- Частотности в языке
- Релевантности для пользователя
- Связи с уже изученными словами
