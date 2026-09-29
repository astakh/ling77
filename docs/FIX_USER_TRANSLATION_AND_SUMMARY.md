# Исправление проблем с отображением перевода пользователя и страницы саммари

## Дата
2026-09-29

## Проблемы

### Проблема 1: Не отображается перевод пользователя
На странице результата упражнения не показывался перевод пользователя для каждого слова, даже если он был сохранён в базе данных.

### Проблема 2: Страница саммари не отображается
При переходе на страницу `/lesson/summary` появлялось предупреждение React:
```
You should call navigate() in a React.useEffect(), not when your component is first rendered.
```
И страница сразу перенаправляла на dashboard, не показывая статистику урока.

## Причины

### Причина 1: Не возвращался user_fragment в idempotency ответе
В файле `backend/routes/lesson.py` в блоке idempotency (когда упражнение уже было оценено) при создании `ExerciseWordResponse` не передавалось поле `user_fragment`.

**Код до исправления (строки 391-402):**
```python
ExerciseWordResponse(
    word_id=ew.word_id,
    is_target=ew.is_target,
    is_new=ew.is_new,
    surface_form=ew.surface_form,
    translation=words_map[ew.word_id].translations[0] if ew.word_id in words_map and words_map[ew.word_id].translations else None,
    result=ew.result,
    # user_fragment отсутствовал!
    stage_before=ew.stage_before,
    stage_after=ew.stage_after,
)
```

### Причина 2: navigate() вызывался при первом рендере
В файле `src/pages/LessonSummaryPage.tsx` проверка условия и вызов `navigate()` происходили непосредственно в теле компонента, а не в `useEffect`.

**Код до исправления (строки 9-12):**
```typescript
if (!currentLesson || currentLesson.status !== 'completed') {
  navigate('/dashboard');  // Вызывается при каждом рендере!
  return null;
}
```

### Причина 3: currentLesson очищался слишком рано
В файле `src/store/useStore.ts` функция `completeLesson()` очищала `currentLesson`, что приводило к тому, что при переходе на страницу summary она не могла отобразить данные.

**Код до исправления (строки 383-387):**
```typescript
completeLesson: async () => {
  // Lesson is auto-completed by backend when last exercise is evaluated
  set({ currentLesson: null, currentExerciseIndex: 0 });  // Очищает currentLesson!
},
```

## Решения

### Решение 1: Добавлен user_fragment в idempotency ответ
**Файл:** `backend/routes/lesson.py` (строка 399)

Добавлена передача поля `user_fragment`:
```python
ExerciseWordResponse(
    word_id=ew.word_id,
    is_target=ew.is_target,
    is_new=ew.is_new,
    surface_form=ew.surface_form,
    translation=words_map[ew.word_id].translations[0] if ew.word_id in words_map and words_map[ew.word_id].translations else None,
    result=ew.result,
    user_fragment=ew.user_fragment,  # Добавлено!
    stage_before=ew.stage_before,
    stage_after=ew.stage_after,
)
```

### Решение 2: navigate() перенесён в useEffect
**Файл:** `src/pages/LessonSummaryPage.tsx` (строки 10-18)

Проверка условия и вызов `navigate()` перенесены в `useEffect`:
```typescript
useEffect(() => {
  if (!currentLesson || currentLesson.status !== 'completed') {
    navigate('/dashboard');
  }
}, [currentLesson, navigate]);

if (!currentLesson || currentLesson.status !== 'completed') {
  return null;  // Просто возвращаем null, не вызывая navigate
}
```

### Решение 3: Добавлена функция clearCurrentLesson
**Файл:** `src/store/useStore.ts`

1. Функция `completeLesson()` больше не очищает `currentLesson`:
```typescript
completeLesson: async () => {
  // Lesson is auto-completed by backend when last exercise is evaluated
  // Don't clear currentLesson here - it's needed for the summary page
  // The summary page will handle cleanup
  set({ currentExerciseIndex: 0 });
},
```

2. Добавлена новая функция `clearCurrentLesson()`:
```typescript
clearCurrentLesson: () => {
  set({ currentLesson: null, currentExerciseIndex: 0 });
},
```

3. В `LessonSummaryPage` добавлена кнопка, которая вызывает `clearCurrentLesson()` при переходе на dashboard:
```typescript
const handleGoToDashboard = () => {
  clearCurrentLesson();
  navigate('/dashboard');
};

<button onClick={handleGoToDashboard}>
  На главную
</button>
```

## Изменённые файлы

### Backend
- `backend/routes/lesson.py` - добавлен `user_fragment` в idempotency ответ

### Frontend
- `src/store/useStore.ts` - изменена `completeLesson()`, добавлена `clearCurrentLesson()`
- `src/pages/LessonSummaryPage.tsx` - перенесён `navigate()` в `useEffect`, добавлена обработка кнопки "На главную"

## Как это работает теперь

### Поток данных для перевода пользователя

1. Пользователь вводит перевод предложения
2. Frontend отправляет запрос на `/lesson/evaluate`
3. Backend вызывает LLM для оценки перевода
4. LLM возвращает `user_fragment` для каждого слова (как пользователь перевёл это слово)
5. Backend сохраняет `user_fragment` в `LessonExerciseWord.user_fragment`
6. Backend возвращает `user_fragment` в ответе API
7. Frontend отображает `user_fragment` на странице результата

### Поток данных для страницы саммари

1. Пользователь завершает последнее упражнение
2. Frontend вызывает `completeLesson()` (не очищает `currentLesson`)
3. Frontend переходит на `/lesson/summary`
4. `LessonSummaryPage` отображает статистику из `currentLesson`
5. Пользователь нажимает "На главную"
6. Вызывается `clearCurrentLesson()` (очищает `currentLesson`)
7. Frontend переходит на `/dashboard`

## Тестирование

### Тест 1: Перевод пользователя
1. Перезапустите backend: `uvicorn main:app --reload`
2. Начните урок
3. Переведите предложение
4. На странице результата проверьте блок "📝 Оценка слов"
5. Для каждого слова должен отображаться "Ваш перевод: ..."

### Тест 2: Страница саммари
1. Пройдите урок до конца
2. После последнего упражнения должен произойти переход на `/lesson/summary`
3. Должна отобразиться статистика:
   - Процент точности
   - Стрик
   - Количество новых слов
   - Количество повторённых слов
   - Список результатов по каждому упражнению
4. Нажмите "На главную"
5. Должен произойти переход на `/dashboard`
6. В консоли браузера не должно быть предупреждений React

## Проверка в логах

### Backend логи
При оценке упражнения должны быть логи:
```
📝 Exercise words response: 2 words
   Word 0: suggest - correct - предлагать
   Word 1: consider - incorrect - рассматривать
```

### Frontend логи
В консоли браузера должны быть логи:
```
Word 0: {
  word_id: 1,
  surface_form: "suggest",
  translation: "предлагать",
  result: "correct",
  user_fragment: "предложил"  // Должно быть заполнено!
}
```

## Преимущества исправлений

1. **Полная информация** - пользователь видит свой перевод для каждого слова
2. **Лучший UX** - нет предупреждений React в консоли
3. **Правильная навигация** - страница саммари корректно отображается
4. **Чистое состояние** - `currentLesson` очищается только когда нужно

## Обратная совместимость

Все изменения обратно совместимы:
- Backend: добавлено опциональное поле `user_fragment` в ответ
- Frontend: изменена логика навигации, но не структура данных
- База данных: структура таблиц не изменилась

## Дополнительные улучшения (опционально)

В будущем можно добавить:
1. **Сохранение полного перевода предложения** - не только по словам, но и весь перевод
2. **История уроков** - возможность просмотреть статистику прошлых уроков
3. **Экспорт результатов** - возможность сохранить результаты урока в файл

Но текущие исправления решают основные проблемы и улучшают UX.
