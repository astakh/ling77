# Добавление отображения полного перевода пользователя

## Проблема

На странице результата оценки упражнения отображался только правильный перевод предложения, но не показывался **полный перевод пользователя**.

## Причина

Backend сохранял полный перевод пользователя в поле `user_translation` таблицы `lesson_exercises`, но не возвращал его в ответе API `/lesson/evaluate`.

## Решение

### 1. Backend изменения

#### Файл: `backend/schemas.py`

Добавлено поле `user_translation` в схему `EvaluateResponse`:

```python
class EvaluateResponse(BaseModel):
    exercise_id: int
    result: Literal["correct", "typo", "incorrect"]
    words: list["ExerciseWordResponse"]
    user_translation: str  # ← Добавлено
    reference_translation: str
    is_last: bool
    new_suggested_words: list[NewSuggestedWord] = []
```

#### Файл: `backend/routes/lesson.py`

Обновлён endpoint `/lesson/evaluate` для возврата `user_translation`:

```python
return EvaluateResponse(
    exercise_id=exercise.id,
    result=overall_result,
    words=exercise_words_response,
    user_translation=body.user_translation,  # ← Добавлено
    reference_translation=exercise.reference_translation,
    is_last=is_last,
    new_suggested_words=filtered_new_suggested_words,
)
```

### 2. Frontend изменения

#### Файл: `src/api/client.ts`

Обновлён тип ответа API для метода `evaluate`:

```typescript
evaluate: (exerciseId: number, userTranslation: string, idempotencyKey?: string) =>
  request<{
    exercise_id: number;
    result: 'correct' | 'typo' | 'incorrect';
    words: any[];
    user_translation: string;  // ← Добавлено
    reference_translation: string;
    is_last: boolean;
    new_suggested_words: Array<{ word: string; translation: string }>;
  }>('/lesson/evaluate', {
    method: 'POST',
    body: JSON.stringify({ exercise_id: exerciseId, user_translation: userTranslation }),
    headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined,
  }),
```

#### Файл: `src/store/useStore.ts`

Обновлён метод `evaluateExercise` для передачи `userTranslation`:

```typescript
evaluateExercise: async (exerciseId: number, translation: string) => {
  set({ isLoading: true, error: null });
  try {
    const response = await api.lesson.evaluate(exerciseId, translation);
    console.log('📥 Backend response for evaluation:', response);
    console.log('📝 Words with user_fragment:', response.words.map((w: any) => ({
      word: w.surface_form || w.surfaceForm,
      result: w.result,
      user_fragment: w.user_fragment || w.userFragment,
      translation: w.translation
    })));
    set({ isLoading: false });
    return {
      result: response.result,
      words: response.words,
      isLast: response.is_last,
      userTranslation: response.user_translation,  // ← Добавлено
      referenceTranslation: response.reference_translation,
      newSuggestedWords: response.new_suggested_words || [],
    };
  } catch (error: any) {
    set({ error: error.detail || 'Failed to evaluate exercise', isLoading: false });
    throw error;
  }
},
```

#### Файл: `src/pages/ExercisePage.tsx`

Добавлен блок для отображения полного перевода пользователя:

```tsx
{/* Show user's translation */}
{resultData && resultData.userTranslation && (
  <div className="bg-blue-50 rounded-xl p-4 border border-blue-200 w-full mb-4">
    <p className="text-xs text-blue-600 uppercase tracking-wide mb-1 font-medium">Ваш перевод</p>
    <p className="text-gray-800 font-medium">{resultData.userTranslation}</p>
  </div>
)}

{/* Show correct answer */}
{resultData && (
  <div className="bg-white rounded-xl p-4 border border-gray-200 w-full mb-6">
    <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Правильный перевод</p>
    <p className="text-gray-800 font-medium">{resultData.referenceTranslation}</p>
  </div>
)}
```

## Результат

Теперь на странице результата оценки упражнения отображаются:

1. **Ваш перевод** (голубой блок) - полный перевод предложения, который ввёл пользователь
2. **Правильный перевод** (белый блок) - эталонный перевод
3. **📝 Оценка слов** - детальная оценка каждого целевого слова с переводами

### Пример отображения

```
┌─────────────────────────────────────┐
│          ✓ Отлично!                 │
│    Все 2 слов переведены правильно! │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ВАШ ПЕРЕВОД                         │
│ Нам нужно учесть погоду перед       │
│ планированием нашей поездки на пляж.│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ПРАВИЛЬНЫЙ ПЕРЕВОД                  │
│ Нам нужно учесть погоду перед       │
│ планированием нашей поездки на пляж.│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📝 ОЦЕНКА СЛОВ                      │
│                                     │
│ weather ✓ Правильно                 │
│ Ваш перевод: погоду                 │
│                                     │
│ consider ✓ Правильно                │
│ Ваш перевод: учесть                  │
└─────────────────────────────────────┘
```

## Тестирование

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Перезапустите frontend
```bash
npm run dev
```

### 3. Проверьте отображение
1. Начните урок
2. Переведите предложение
3. Нажмите "Проверить"
4. На странице результата должны увидеть:
   - Голубой блок "Ваш перевод" с полным переводом
   - Белый блок "Правильный перевод" с эталонным переводом
   - Блок "📝 Оценка слов" с детальной оценкой каждого слова

### 4. Проверьте логи
В консоли браузера должны быть логи:
```
📥 Backend response for evaluation: {
  exercise_id: 30,
  result: 'incorrect',
  words: [...],
  user_translation: 'нам нужно учесть погоду...',
  reference_translation: 'Нам нужно учесть погоду...',
  ...
}
```

## Изменённые файлы

### Backend
- `backend/schemas.py` - добавлено поле `user_translation` в `EvaluateResponse`
- `backend/routes/lesson.py` - обновлён endpoint `/lesson/evaluate`

### Frontend
- `src/api/client.ts` - обновлён тип ответа API
- `src/store/useStore.ts` - обновлён метод `evaluateExercise`
- `src/pages/ExercisePage.tsx` - добавлен блок отображения перевода пользователя

## Преимущества

1. **Полная обратная связь** - пользователь видит свой полный перевод
2. **Сравнение с эталоном** - легко сравнить свой перевод с правильным
3. **Лучшее обучение** - видно, как переведено предложение целиком
4. **Контекст** - понятнее, как отдельные слова вписываются в общий перевод

## Связанные документы

- `docs/FIX_USER_TRANSLATION_AND_SUMMARY.md` - предыдущие исправления
- `docs/FIX_WORD_EVALUATION_DISPLAY.md` - отображение оценки слов
- `docs/EXERCISE_RESULT_UPDATE.md` - обновление страницы результата
