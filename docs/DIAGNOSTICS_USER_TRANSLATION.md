# Диагностика проблемы с отображением перевода пользователя

## Проблема
На странице результата упражнения не отображается перевод пользователя для каждого слова.

## Добавленное логирование

Для диагностики проблемы добавлено детальное логирование на всех уровнях обработки данных:

### Backend (Python)

#### 1. Логирование полного ответа LLM
**Файл:** `backend/routes/lesson.py` (строки 454-468)

```python
logger.info(f"📊 FULL LLM Response: {llm_result}")
logger.info(f"   Overall result: {overall_result}")
logger.info(f"   Evaluations count: {len(evaluations)}")

# Логируем каждое evaluation детально
for i, eval_item in enumerate(evaluations):
    logger.info(f"   📝 Evaluation {i}:")
    logger.info(f"      word_lemma: '{eval_item.get('word_lemma', 'MISSING')}'")
    logger.info(f"      result: '{eval_item.get('result', 'MISSING')}'")
    logger.info(f"      user_fragment: '{eval_item.get('user_fragment', 'MISSING')}'")
    logger.info(f"      ALL KEYS: {list(eval_item.keys())}")
```

**Что показывает:**
- Полный JSON ответ от LLM
- Количество оценённых слов
- Для каждого слова: lemma, результат, user_fragment и все ключи

#### 2. Логирование поиска оценки для каждого слова
**Файл:** `backend/routes/lesson.py` (строки 482-488)

```python
logger.info(f"🔍 Looking for evaluation of word '{word.lemma}':")
logger.info(f"   Found eval_data: {eval_data}")
logger.info(f"   eval_data keys: {list(eval_data.keys())}")
```

**Что показывает:**
- Какое слово ищем
- Какие данные найдены для этого слова
- Все ключи в найденных данных

#### 3. Логирование сохранения в базу данных
**Файл:** `backend/routes/lesson.py` (строка 496)

```python
logger.info(f"💾 Saving word '{word.lemma}': result={result_str}, user_fragment='{user_fragment}'")
```

**Что показывает:**
- Какое слово сохраняется
- Результат оценки
- Значение user_fragment, которое будет сохранено

#### 4. Логирование ответа API
**Файл:** `backend/routes/lesson.py` (строки 525-527)

```python
logger.info(f"📝 Exercise words response: {len(exercise_words_response)} words")
for i, ewr in enumerate(exercise_words_response):
    logger.info(f"   Word {i}: {ewr.surface_form} - {ewr.result} - {ewr.translation} - user_fragment='{ewr.user_fragment}'")
```

**Что показывает:**
- Сколько слов возвращается в ответе
- Для каждого слова: surface_form, result, translation, user_fragment

### Frontend (TypeScript)

#### 1. Логирование ответа от backend
**Файл:** `src/store/useStore.ts` (строки 359-366)

```typescript
console.log('📥 Backend response for evaluation:', response);
console.log('📝 Words with user_fragment:', response.words.map((w: any) => ({
  word: w.surface_form || w.surfaceForm,
  result: w.result,
  user_fragment: w.user_fragment || w.userFragment,
  translation: w.translation
})));
```

**Что показывает:**
- Полный ответ от backend
- Массив слов с извлечёнными user_fragment

#### 2. Логирование в ExercisePage
**Файл:** `src/pages/ExercisePage.tsx` (строки 79-81)

```typescript
console.log('🎯 ExercisePage received result:', result);
console.log('📝 Words in result:', result.words);
```

**Что показывает:**
- Результат, полученный из store
- Массив слов в результате

#### 3. Логирование при рендеринге каждого слова
**Файл:** `src/pages/ExercisePage.tsx` (строки 333-338)

```typescript
console.log(`🔍 Word ${idx} rendering:`, word);
console.log(`   user_fragment:`, word.user_fragment);
console.log(`   userFragment:`, word.userFragment);
// Маппим snake_case из backend в camelCase для frontend
const userFragment = word.user_fragment || word.userFragment;
console.log(`   Mapped userFragment:`, userFragment);
```

**Что показывает:**
- Объект слова при рендеринге
- Значение user_fragment (snake_case)
- Значение userFragment (camelCase)
- Итоговое значение после маппинга

## Как диагностировать проблему

### Шаг 1: Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### Шаг 2: Перезапустите frontend
```bash
npm run dev
```

### Шаг 3: Откройте DevTools
- Нажмите F12
- Перейдите на вкладку Console

### Шаг 4: Пройдите урок и переведите предложение

### Шаг 5: Проверьте логи

#### В терминале backend должны быть:

1. **Полный ответ LLM:**
```
📊 FULL LLM Response: {...}
   Overall result: correct
   Evaluations count: 2
   📝 Evaluation 0:
      word_lemma: 'suggest'
      result: 'correct'
      user_fragment: 'предложил'
      ALL KEYS: ['word_lemma', 'result', 'user_fragment']
```

2. **Поиск оценки для каждого слова:**
```
🔍 Looking for evaluation of word 'suggest':
   Found eval_data: {'word_lemma': 'suggest', 'result': 'correct', 'user_fragment': 'предложил'}
   eval_data keys: ['word_lemma', 'result', 'user_fragment']
💾 Saving word 'suggest': result=correct, user_fragment='предложил'
```

3. **Ответ API:**
```
📝 Exercise words response: 2 words
   Word 0: suggest - correct - предлагать - user_fragment='предложил'
```

#### В консоли браузера должны быть:

1. **Ответ от backend:**
```
📥 Backend response for evaluation: {
  exercise_id: 1,
  result: 'correct',
  words: [
    {
      word_id: 1,
      surface_form: 'suggest',
      translation: 'предлагать',
      result: 'correct',
      user_fragment: 'предложил'
    }
  ],
  ...
}
📝 Words with user_fragment: [
  {
    word: 'suggest',
    result: 'correct',
    user_fragment: 'предложил',
    translation: 'предлагать'
  }
]
```

2. **Результат в ExercisePage:**
```
🎯 ExercisePage received result: {
  result: 'correct',
  words: [...],
  ...
}
📝 Words in result: [...]
```

3. **Рендеринг каждого слова:**
```
🔍 Word 0 rendering: {
  word_id: 1,
  surface_form: 'suggest',
  translation: 'предлагать',
  result: 'correct',
  user_fragment: 'предложил'
}
   user_fragment: предложил
   userFragment: undefined
   Mapped userFragment: предложил
```

## Возможные проблемы и решения

### Проблема 1: LLM не возвращает user_fragment

**Симптомы:**
В логах backend видно:
```
📝 Evaluation 0:
   word_lemma: 'suggest'
   result: 'correct'
   user_fragment: 'MISSING'
   ALL KEYS: ['word_lemma', 'result']
```

**Решение:**
Проверить промпт в `backend/prompts/evaluate_translation.txt`. Убедиться, что он запрашивает user_fragment:
```
Так же выдели user_fragment — то, как именно перевел ученик это слово в предложении
```

### Проблема 2: user_fragment не сохраняется в базу

**Симптомы:**
В логах backend видно:
```
🔍 Looking for evaluation of word 'suggest':
   Found eval_data: {'word_lemma': 'suggest', 'result': 'correct', 'user_fragment': 'предложил'}
💾 Saving word 'suggest': result=correct, user_fragment=''
```

**Решение:**
Проверить код сохранения в `backend/routes/lesson.py` (строка 493):
```python
ew.user_fragment = user_fragment
```

Убедиться, что `user_fragment` извлекается правильно:
```python
user_fragment = eval_data.get("user_fragment", "")
```

### Проблема 3: user_fragment не возвращается в API ответе

**Симптомы:**
В логах backend видно:
```
💾 Saving word 'suggest': result=correct, user_fragment='предложил'
📝 Exercise words response: 2 words
   Word 0: suggest - correct - предлагать - user_fragment=''
```

**Решение:**
Проверить формирование ответа в `backend/routes/lesson.py` (строка 520):
```python
user_fragment=ew.user_fragment,
```

Убедиться, что поле `user_fragment` есть в схеме `ExerciseWordResponse` в `backend/schemas.py`:
```python
class ExerciseWordResponse(BaseModel):
    ...
    user_fragment: Optional[str] = None
```

### Проблема 4: Frontend не получает user_fragment

**Симптомы:**
В логах backend видно:
```
   Word 0: suggest - correct - предлагать - user_fragment='предложил'
```

В консоли браузера:
```
📥 Backend response for evaluation: {
  words: [
    {
      surface_form: 'suggest',
      result: 'correct',
      // user_fragment отсутствует!
    }
  ]
}
```

**Решение:**
Проверить схему ответа в `backend/schemas.py`. Убедиться, что поле `user_fragment` не исключено из ответа.

Проверить маппинг в `src/api/client.ts`:
```typescript
evaluate: (exerciseId: number, userTranslation: string) =>
  request<{
    exercise_id: number;
    result: string;
    words: Array<{
      word_id: number;
      is_target: boolean;
      is_new: boolean;
      surface_form: string;
      translation: string | null;
      result: string | null;
      user_fragment: string | null;  // Должно быть!
      stage_before: number;
      stage_after: number;
    }>;
    reference_translation: string;
    is_last: boolean;
    new_suggested_words: Array<{
      word: string;
      translation: string;
    }>;
  }>(`/lesson/${exerciseId}/evaluate`, {
    method: 'POST',
    body: JSON.stringify({
      user_translation: userTranslation,
    }),
  }),
```

### Проблема 5: Frontend не отображает user_fragment

**Симптомы:**
В консоли браузера видно:
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

Но на странице не отображается.

**Решение:**
Проверить рендеринг в `src/pages/ExercisePage.tsx` (строки 365-375):
```typescript
{!isCorrect && (
  <div className="mt-2 space-y-1">
    <div className="text-sm">
      <span className="text-gray-500">Ваш перевод: </span>
      <span className={`font-medium ${
        isTypo ? 'text-amber-600' : 'text-red-500'
      }`}>
        {userFragment || '—'}
      </span>
    </div>
    ...
  </div>
)}
```

Убедиться, что условие `{!isCorrect && ...}` не блокирует отображение для правильных ответов.

Если нужно показывать перевод пользователя и для правильных ответов, измените условие:
```typescript
{userFragment && (
  <div className="mt-2 space-y-1">
    <div className="text-sm">
      <span className="text-gray-500">Ваш перевод: </span>
      <span className="font-medium text-green-600">
        {userFragment}
      </span>
    </div>
    ...
  </div>
)}
```

## Проверка базы данных

Можно проверить, сохраняются ли user_fragment в базу данных:

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

Если `user_fragment` пустой в базе данных, значит проблема на этапе сохранения (Проблема 2).

## Проверка API напрямую

Можно проверить API напрямую с помощью curl:

```bash
curl -X POST http://localhost:8000/lesson/1/evaluate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_translation": "я предложил"}'
```

Проверить, что в ответе есть поле `user_fragment` для каждого слова.

## Ожидаемый результат

После исправления проблемы на странице результата упражнения должно отображаться:

```
suggest                           ✓ Правильно
Ваш перевод: предложил

consider                          ✗ Неправильно
Ваш перевод: важный
Правильный перевод: рассматривать
```

## Дополнительные проверки

### Проверка промпта LLM

Убедиться, что промпт в `backend/prompts/evaluate_translation.txt` правильно запрашивает user_fragment:

```
Так же выдели user_fragment — то, как именно перевел ученик это слово в предложении (если слова нет вообще - укажи пропущено).

Выдай ответ строго в формате JSON без излишних кавычек и маркеров:
{
  "evaluations": [
    {
      "word_lemma": "слово из списка целевых слов",
      "result": "результат оценки перевода - correct|typo|incorrect",
      "user_fragment": "как оно переведено учеником"
    }
  ],
  ...
}
```

### Проверка схемы Pydantic

Убедиться, что в `backend/schemas.py` поле `user_fragment` определено как опциональное:

```python
class ExerciseWordResponse(BaseModel):
    word_id: int
    is_target: bool
    is_new: bool
    surface_form: str
    translation: Optional[str] = None
    result: Optional[str] = None
    user_fragment: Optional[str] = None  # Опциональное поле
    stage_before: int
    stage_after: int
```

### Проверка маппинга на frontend

Убедиться, что в `src/pages/ExercisePage.tsx` правильно извлекается user_fragment:

```typescript
const userFragment = word.user_fragment || word.userFragment;
```

Это нужно для поддержки обоих форматов (snake_case от backend и camelCase).

## Итоговый чеклист

- [ ] Backend логирует полный ответ LLM
- [ ] Backend логирует поиск оценки для каждого слова
- [ ] Backend логирует сохранение в базу данных
- [ ] Backend логирует ответ API
- [ ] Frontend логирует ответ от backend
- [ ] Frontend логирует рендеринг каждого слова
- [ ] LLM возвращает user_fragment в ответе
- [ ] Backend сохраняет user_fragment в базу данных
- [ ] Backend возвращает user_fragment в API ответе
- [ ] Frontend получает user_fragment из API
- [ ] Frontend отображает user_fragment на странице
- [ ] В базе данных есть значения user_fragment
- [ ] На странице отображается "Ваш перевод: ..."
