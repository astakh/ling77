# Диагностика проблемы с переводом пользователя

## Что добавлено

Добавлено детальное логирование на всех уровнях обработки данных:

### Backend логи (в терминале)
1. Полный ответ от LLM
2. Поиск оценки для каждого слова
3. Сохранение в базу данных
4. Ответ API

### Frontend логи (в консоли браузера)
1. Ответ от backend
2. Результат в ExercisePage
3. Рендеринг каждого слова

## Как протестировать

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Перезапустите frontend
```bash
npm run dev
```

### 3. Откройте DevTools
- Нажмите F12
- Перейдите на вкладку Console

### 4. Пройдите урок и переведите предложение

### 5. Проверьте логи

#### В терминале backend ищите:

```
📊 FULL LLM Response: {...}
   📝 Evaluation 0:
      word_lemma: 'suggest'
      result: 'correct'
      user_fragment: 'предложил'
      ALL KEYS: ['word_lemma', 'result', 'user_fragment']

🔍 Looking for evaluation of word 'suggest':
   Found eval_data: {'word_lemma': 'suggest', 'result': 'correct', 'user_fragment': 'предложил'}

💾 Saving word 'suggest': result=correct, user_fragment='предложил'

📝 Exercise words response: 2 words
   Word 0: suggest - correct - предлагать - user_fragment='предложил'
```

#### В консоли браузера ищите:

```
📥 Backend response for evaluation: {
  words: [
    {
      surface_form: 'suggest',
      user_fragment: 'предложил'
    }
  ]
}

🔍 Word 0 rendering: {
  surface_form: 'suggest',
  user_fragment: 'предложил'
}
   user_fragment: предложил
   userFragment: undefined
   Mapped userFragment: предложил
```

## Возможные проблемы

### Если LLM не возвращает user_fragment

В логах backend увидите:
```
📝 Evaluation 0:
   word_lemma: 'suggest'
   result: 'correct'
   user_fragment: 'MISSING'
```

**Решение:** Проверить промпт в `backend/prompts/evaluate_translation.txt`

### Если user_fragment не сохраняется

В логах backend увидите:
```
🔍 Found eval_data: {'word_lemma': 'suggest', 'result': 'correct', 'user_fragment': 'предложил'}
💾 Saving word 'suggest': result=correct, user_fragment=''
```

**Решение:** Проверить код сохранения в `backend/routes/lesson.py`

### Если user_fragment не возвращается в API

В логах backend увидите:
```
💾 Saving word 'suggest': result=correct, user_fragment='предложил'
📝 Exercise words response: 2 words
   Word 0: suggest - correct - предлагать - user_fragment=''
```

**Решение:** Проверить схему ответа в `backend/schemas.py`

### Если frontend не получает user_fragment

В консоли браузера увидите:
```
📥 Backend response for evaluation: {
  words: [
    {
      surface_form: 'suggest'
      // user_fragment отсутствует!
    }
  ]
}
```

**Решение:** Проверить типизацию в `src/api/client.ts`

### Если frontend не отображает user_fragment

В консоли браузера увидите:
```
🔍 Word 0 rendering: {
  surface_form: 'suggest',
  user_fragment: 'предложил'
}
   Mapped userFragment: предложил
```

Но на странице не отображается.

**Решение:** Проверить рендеринг в `src/pages/ExercisePage.tsx`

## Проверка базы данных

```sql
SELECT 
    ew.surface_form,
    ew.result,
    ew.user_fragment,
    w.translations
FROM lesson_exercise_words ew
JOIN words w ON ew.word_id = w.id
WHERE ew.is_target = true
ORDER BY ew.id DESC
LIMIT 10;
```

## Подробная документация

Полная инструкция по диагностике: `docs/DIAGNOSTICS_USER_TRANSLATION.md`

## Что делать дальше

1. Перезапустите backend и frontend
2. Пройдите урок
3. Скопируйте логи из терминала backend и консоли браузера
4. Определите на каком этапе теряется user_fragment
5. Примените соответствующее решение из документации
