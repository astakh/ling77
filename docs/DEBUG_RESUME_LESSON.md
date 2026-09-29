# 🐛 Отладка проблемы с "Продолжить урок"

## Проблема
При нажатии "Продолжить урок" на дашборде страница просто перезагружается вместо перехода к упражнению.

## Причина
`currentLesson` хранится только в памяти store (Zustand) и теряется при перезагрузке страницы. Когда пользователь нажимает "Продолжить урок", `ExercisePage` проверяет `currentLesson` в store, видит что его нет, и редиректит обратно на dashboard.

## Решение
Добавлен backend endpoint `/lesson/current` который возвращает текущий урок из базы данных. При загрузке `ExercisePage` проверяет store, и если урока там нет - загружает его с backend.

## Что изменено

### Backend
- ✅ Добавлен endpoint `GET /lesson/current` в `backend/routes/lesson.py`
- ✅ Возвращает текущий урок с упражнениями и словами
- ✅ Добавлено логирование

### Frontend
- ✅ Добавлен метод `api.lesson.getCurrent()` в `src/api/client.ts`
- ✅ Добавлен метод `loadCurrentLesson()` в `src/store/useStore.ts`
- ✅ Обновлён `ExercisePage` для загрузки урока с backend
- ✅ Добавлено логирование в `DashboardPage` и `ExercisePage`

## Как тестировать

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Перезапустите frontend
```bash
npm run dev
```

### 3. Создайте урок
1. Откройте http://localhost:3000
2. Нажмите "Начать урок"
3. Пройдите превью и начните урок
4. Увидите первое упражнение

### 4. Перезагрузите страницу
1. Нажмите F5 или Ctrl+R
2. Вы должны вернуться на dashboard (урок потерян из store)

### 5. Нажмите "Продолжить урок"
1. На dashboard нажмите кнопку "Продолжить урок"
2. Откройте DevTools (F12) → Console
3. Вы должны увидеть логи:

```
🎯 Dashboard CTA clicked
   summary: {cta: "resume", currentLessonId: 123, ...}
   Resuming lesson #123

🔍 ExercisePage: checking current lesson...
   currentLesson: null
   No lesson in store, loading from backend...

📥 Loading current lesson from backend...
   Found lesson #1 with 3 exercises
   Resuming from exercise 1
   Lesson loaded successfully
```

### 6. Проверьте логи backend
В терминале backend должны быть логи:

```
🔍 Getting current lesson for user 1
   ✅ Found lesson #1 (id=123, status=in_progress)
   Loaded 3 exercises
```

## Ожидаемое поведение

1. ✅ Пользователь начинает урок
2. ✅ Урок сохраняется в БД со статусом `in_progress`
3. ✅ При перезагрузке страницы пользователь возвращается на dashboard
4. ✅ На dashboard показывается кнопка "Продолжить урок"
5. ✅ При нажатии кнопки `ExercisePage` загружает урок с backend
6. ✅ Пользователь продолжает урок с того же упражнения

## Если не работает

### Проверьте что урок создан
```sql
-- В psql
SELECT id, lesson_number, status, started_local_date 
FROM lessons 
WHERE learning_profile_id = (SELECT id FROM learning_profiles WHERE user_id = 1)
ORDER BY lesson_number DESC
LIMIT 5;
```

Должен быть урок со статусом `in_progress`.

### Проверьте backend endpoint
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/lesson/current
```

Должен вернуть JSON с уроком.

### Проверьте консоль браузера
Откройте DevTools (F12) → Console и посмотрите логи. Если видите ошибки - покажите их.

### Проверьте Network tab
В DevTools → Network найдите запрос `/lesson/current` и проверьте:
- Status code: должен быть 200
- Response: должен содержать объект `lesson` с упражнениями

## Логирование

### Frontend логи (в консоли браузера)
- `🎯 Dashboard CTA clicked` - нажата кнопка на dashboard
- `🔍 ExercisePage: checking current lesson...` - проверка урока в ExercisePage
- `📥 Loading current lesson from backend...` - загрузка урока с backend
- `✅ Lesson loaded successfully` - урок успешно загружен
- `❌ No lesson found` - урок не найден

### Backend логи (в терминале)
- `🔍 Getting current lesson for user X` - запрос текущего урока
- `✅ Found lesson #X` - урок найден
- `❌ No in-progress lesson found` - урок не найден
- `Loaded X exercises` - загружено упражнений

## Следующие шаги

Если проблема не решена:
1. Покажите логи из консоли браузера
2. Покажите логи из терминала backend
3. Покажите результат `curl` запроса к `/lesson/current`
4. Покажите результат SQL запроса к таблице `lessons`
