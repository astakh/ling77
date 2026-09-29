# ✅ Новый алгоритм выбора слов для урока

## Что изменилось

Алгоритм выбора слов для урока полностью переработан согласно требованиям:

### Новые правила
1. ✅ **Общее количество слов = `words_per_lesson`** (из настроек пользователя)
2. ✅ **Гарантия минимум 1 нового слова** в каждом уроке
3. ✅ **Если не хватает слов**, добавляются новые слова до `words_per_lesson`
4. ✅ **Если due слов слишком много**, берутся самые перезревшие (most overdue)

## Как работает алгоритм

```
Цель: words_per_lesson слов

Шаг 1: Гарантируем минимум 1 новое слово
   ↓
Шаг 2: Берём due слова (самые перезревшие)
   ↓
Шаг 3: Заполняем остаток новыми словами
```

### Приоритет due слов
Due слова сортируются по **перезрелости** (overdue):
```python
overdue = current_lesson - due_lesson_number
```
Чем больше `overdue`, тем дольше слово ждёт повторения и тем выше приоритет.

## Примеры

### Пример 1: 15 due слов, 20 new слов, target = 10
```
1. Берём 1 новое слово (гарантия)
2. Берём 9 due слов (самые перезревшие из 15)
3. Итого: 9 due + 1 new = 10 слов ✓
```

### Пример 2: 3 due слова, 20 new слов, target = 10
```
1. Берём 1 новое слово (гарантия)
2. Берём 3 due слова (все доступные)
3. Берём ещё 6 новых слов
4. Итого: 3 due + 7 new = 10 слов ✓
```

### Пример 3: 0 due слов, 20 new слов, target = 10
```
1. Берём 1 новое слово (гарантия)
2. Нет due слов
3. Берём ещё 9 новых слов
4. Итого: 0 due + 10 new = 10 слов ✓
```

## Что нужно сделать

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Проверьте настройки
1. Откройте http://localhost:3000
2. Перейдите в настройки (⚙️)
3. Убедитесь, что "Слов в уроке" установлено (например, 10)

### 3. Начните урок
1. Вернитесь на дашборд
2. Нажмите "Начать урок"
3. Проверьте количество слов на странице превью

### 4. Проверьте логи
В логах backend должно быть:
```
📝 Exercise words response: 10 words
```

## Проверка в базе данных

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

Ожидаемый результат:
- `total_words` = `words_per_lesson`
- `new_words` >= 1 (гарантия)
- `due_words` + `new_words` = `total_words`

## Документация

- **Полная документация:** `docs/NEW_WORD_SELECTION_ALGORITHM.md`
- **Предыдущее исправление:** `docs/FIX_WORDS_PER_LESSON.md`

## Изменённые файлы

- `backend/routes/lesson.py` - функция `select_words_for_lesson()`

## Преимущества

✅ **Гибкость** - адаптируется к количеству доступных слов  
✅ **Эффективность** - приоритет перезревших слов  
✅ **Разнообразие** - гарантия новых слов в каждом уроке  
✅ **Настраиваемость** - использует `words_per_lesson` из настроек  

Готово к тестированию! 🎉
