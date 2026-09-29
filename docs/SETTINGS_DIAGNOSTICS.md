# Диагностика проблемы сохранения настроек

## Проблема
Настройки успешно сохраняются в backend (видно в логах), но изменения не отображаются на фронтенде после перезагрузки страницы настроек.

## Добавленное логирование

### Backend (уже работает)
```
📝 Updating settings for user 2
   Request body: level=A2, words_per_lesson=8, lessons_per_day=10, dictionary_id=1
   Current profile: level=A1, words_per_lesson=8, daily_lesson_limit=5, dictionary_id=1
   ✓ Updated level to A2
   ✓ Updated words_per_lesson to 8
   ✓ Updated daily_lesson_limit to 10
✅ Settings saved successfully for user 2
   New profile: level=A2, words_per_lesson=8, daily_lesson_limit=10, dictionary_id=1
```

### Frontend (добавлено)

#### SettingsPage.tsx
```typescript
// При загрузке страницы
🔍 SettingsPage: Current profile from store: {...}
🔍 SettingsPage: Initial state: {level, wordsPerLesson, lessonsPerDay, dictionaryId}

// При изменении profile
🔍 SettingsPage: Profile changed, updating state: {...}

// При сохранении
💾 handleSave: Starting save process
💾 handleSave: Current state: {...}
📝 handleSave: Sending to backend: {...}
✅ handleSave: Backend response: {...}
🔄 handleSave: Updating profile in store: {...}
🔄 handleSave: Old profile: {...}
🔄 handleSave: Store updated, verifying: {...}
⏰ handleSave: Scheduling navigation to dashboard in 1 second
🚀 handleSave: Navigating to dashboard
🏁 handleSave: Save process completed
```

#### useStore.ts
```typescript
📊 getDashboardSummary: Loading dashboard summary
📊 getDashboardSummary: Current profile: {...}
📊 getDashboardSummary: Backend response: {...}
```

#### DashboardPage.tsx
```typescript
🏠 DashboardPage: Component mounted
🏠 DashboardPage: Current profile: {...}
🏠 DashboardPage: Loading dashboard data
🏠 DashboardPage: Dashboard data loaded: {...}
```

## Как тестировать

### Шаг 1: Перезапустите frontend
```bash
npm run dev
```

### Шаг 2: Откройте консоль браузера
- Нажмите F12
- Перейдите на вкладку Console
- Очистите консоль (кнопка 🚫)

### Шаг 3: Перейдите на страницу настроек
- Нажмите на иконку ⚙️ на дашборде
- Обратите внимание на логи в консоли

**Ожидаемые логи при загрузке страницы настроек:**
```
🔍 SettingsPage: Current profile from store: {level: "A1", wordsPerLesson: 8, ...}
🔍 SettingsPage: Initial state: {level: "A1", wordsPerLesson: 8, lessonsPerDay: 5, dictionaryId: 1}
🔍 SettingsPage: useEffect - loading dictionaries
```

### Шаг 4: Измените настройки
- Измените уровень на B1
- Измените количество слов в уроке на 10
- Измените количество уроков в день на 3
- Выберите другой словарь

### Шаг 5: Нажмите "Сохранить настройки"
- Обратите внимание на логи в консоли

**Ожидаемые логи при сохранении:**
```
💾 handleSave: Starting save process
💾 handleSave: Current state: {level: "B1", wordsPerLesson: 10, lessonsPerDay: 3, dictionaryId: 2}
📝 handleSave: Sending to backend: {level: "B1", words_per_lesson: 10, lessons_per_day: 3, dictionary_id: 2}
✅ handleSave: Backend response: {status: "ok"}
🔄 handleSave: Updating profile in store: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
🔄 handleSave: Old profile: {level: "A1", wordsPerLesson: 8, dailyLessonLimit: 5, dictionaryId: 1}
🔄 handleSave: Store updated, verifying: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
⏰ handleSave: Scheduling navigation to dashboard in 1 second
🚀 handleSave: Navigating to dashboard
🏁 handleSave: Save process completed
```

### Шаг 6: Проверьте дашборд
- После возврата на дашборд обратите внимание на логи

**Ожидаемые логи:**
```
🏠 DashboardPage: Component mounted
🏠 DashboardPage: Current profile: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
🏠 DashboardPage: Loading dashboard data
📊 getDashboardSummary: Loading dashboard summary
📊 getDashboardSummary: Current profile: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
📊 getDashboardSummary: Backend response: {...}
🏠 DashboardPage: Dashboard data loaded: {...}
```

### Шаг 7: Вернитесь на страницу настроек
- Снова нажмите на иконку ⚙️
- Проверьте, отображаются ли новые значения

**Ожидаемые логи:**
```
🔍 SettingsPage: Current profile from store: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
🔍 SettingsPage: Initial state: {level: "B1", wordsPerLesson: 10, lessonsPerDay: 3, dictionaryId: 2}
🔍 SettingsPage: Profile changed, updating state: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
```

## Возможные проблемы и решения

### Проблема 1: Profile не обновляется в store
**Симптомы:**
```
🔄 handleSave: Store updated, verifying: {level: "A1", ...}  // Старые значения!
```

**Решение:**
Проверьте, что `useStore.setState()` вызывается правильно. Возможно, нужно использовать функциональное обновление:
```typescript
useStore.setState((state) => ({
  profile: {
    ...state.profile,
    level,
    wordsPerLesson,
    dailyLessonLimit: lessonsPerDay,
    dictionaryId,
  }
}));
```

### Проблема 2: SettingsPage не читает обновлённый profile
**Симптомы:**
```
🔍 SettingsPage: Current profile from store: {level: "A1", ...}  // Старые значения!
```

**Решение:**
Проверьте, что `useEffect` с зависимостью `[profile]` работает:
```typescript
useEffect(() => {
  if (profile) {
    setLevel(profile.level);
    setWordsPerLesson(profile.wordsPerLesson);
    setLessonsPerDay(profile.dailyLessonLimit);
    setDictionaryId(profile.dictionaryId);
  }
}, [profile]);
```

### Проблема 3: Profile не загружается из backend
**Симптомы:**
```
🔍 SettingsPage: Current profile from store: null
```

**Решение:**
Проверьте, что profile загружается при инициализации приложения. Возможно, нужно добавить вызов API для загрузки profile:
```typescript
useEffect(() => {
  if (!profile) {
    loadProfileFromBackend();
  }
}, []);
```

### Проблема 4: useState инициализируется только один раз
**Симптомы:**
- При первом открытии страницы настройки правильные
- После сохранения и возврата настройки старые

**Решение:**
Проблема в том, что `useState` инициализируется только при первом рендере. Нужно добавить `useEffect` для обновления состояния при изменении `profile`:
```typescript
useEffect(() => {
  if (profile) {
    setLevel(profile.level);
    setWordsPerLesson(profile.wordsPerLesson);
    setLessonsPerDay(profile.dailyLessonLimit);
    setDictionaryId(profile.dictionaryId);
  }
}, [profile]);
```

## Проверка в базе данных

Выполните SQL запрос, чтобы убедиться, что настройки сохранены:

```sql
SELECT 
  user_id,
  level,
  words_per_lesson,
  daily_lesson_limit,
  dictionary_id
FROM learning_profiles
WHERE user_id = 2;
```

Ожидаемый результат:
```
 user_id | level | words_per_lesson | daily_lesson_limit | dictionary_id 
---------+-------+------------------+--------------------+---------------
       2 | B1    |               10 |                  3 |             2
```

## Следующие шаги

1. Перезапустите frontend
2. Откройте консоль браузера (F12)
3. Пройдите через все шаги тестирования
4. Скопируйте все логи из консоли
5. Проанализируйте логи на каждом этапе
6. Если проблема не решена, предоставьте полные логи для анализа

## Изменённые файлы

- `src/pages/SettingsPage.tsx` - добавлено логирование и useEffect для обновления состояния
- `src/store/useStore.ts` - добавлено логирование в getDashboardSummary
- `src/pages/DashboardPage.tsx` - добавлено логирование при загрузке
