# Исправление проблем с настройками и отображением перевода

## Дата
2026-09-29

## Проблема 1: Неправильное отображение лимита уроков на дашборде

### Описание
На дашборде отображалось захардкоженное значение `/5` вместо реального лимита уроков из профиля пользователя.

### Причина
В `DashboardPage.tsx` строка 151 содержала захардкоженное значение:
```tsx
{summary.lessonsToday}/5
```

### Решение
1. Добавлен импорт `profile` из `useStore` в `DashboardPage.tsx`
2. Изменено отображение на динамическое значение:
```tsx
{summary.lessonsToday}/{profile?.dailyLessonLimit || 5}
```

### Результат
Теперь дашборд отображает реальный лимит уроков из настроек пользователя.

---

## Проблема 2: Не отображается перевод пользователя на странице оценки

### Описание
После оценки перевода на странице результата не отображался блок "Ваш перевод" для каждого слова.

### Причина
В `ExercisePage.tsx` строка 339 использовала оператор `||` для маппинга:
```tsx
const userFragment = word.user_fragment || word.userFragment;
```

Если `user_fragment` был пустой строкой `""`, то условие возвращало `undefined`, и блок не рендерился.

### Решение
1. Изменена логика маппинга на более явную проверку:
```tsx
const userFragment = word.user_fragment !== undefined 
  ? word.user_fragment 
  : (word.userFragment !== undefined ? word.userFragment : null);
```

2. Изменено условие рендеринга:
```tsx
{userFragment !== null && userFragment !== undefined && (
  <div className="mt-2 space-y-1">
    ...
  </div>
)}
```

3. Добавлено логирование для отладки:
```tsx
console.log(`   Has userFragment:`, userFragment !== null);
```

### Результат
Теперь перевод пользователя отображается корректно, даже если это пустая строка.

---

## Проблема 3: Настройки не сохраняются в store

### Описание
После сохранения настроек и возврата на дашборд, профиль не обновлялся из backend.

### Причина
Profile загружался только при инициализации приложения и не обновлялся после изменения настроек.

### Решение
1. Добавлен endpoint `GET /dictionaries/profile` в backend для получения полного профиля:
```python
@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's learning profile."""
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Learning profile not found")
    
    return {
        "user_id": profile.user_id,
        "level": profile.level,
        "dictionary_id": profile.dictionary_id,
        "daily_lesson_limit": profile.daily_lesson_limit,
        "words_per_lesson": profile.words_per_lesson,
        "last_lesson_number": profile.last_lesson_number,
    }
```

2. Добавлен метод `getProfile()` в frontend API client:
```typescript
getProfile: () =>
  request<{
    user_id: number;
    level: string;
    dictionary_id: number | null;
    daily_lesson_limit: number;
    words_per_lesson: number;
    last_lesson_number: number;
  }>('/dictionaries/profile'),
```

3. Обновлён метод `initialize()` в `useStore.ts` для загрузки profile после инициализации:
```typescript
// Load profile if user is onboarded
if (user.is_onboarded) {
  console.log('🔑 initialize: User is onboarded, loading profile...');
  try {
    const profileData = await api.dictionaries.getProfile();
    console.log('🔑 initialize: Profile loaded:', profileData);
    set({
      profile: {
        userId: String(profileData.user_id),
        level: profileData.level as any,
        dictionaryId: profileData.dictionary_id,
        dailyLessonLimit: profileData.daily_lesson_limit,
        wordsPerLesson: profileData.words_per_lesson,
        lastLessonNumber: profileData.last_lesson_number,
        userWords: [],
      }
    });
  } catch (profileError) {
    console.error('❌ initialize: Failed to load profile:', profileError);
  }
}
```

### Результат
Теперь profile загружается из backend при инициализации приложения и содержит актуальные данные из базы данных.

---

## Изменённые файлы

### Backend
- `backend/routes/dictionaries.py` - добавлен endpoint `GET /dictionaries/profile`

### Frontend
- `src/api/client.ts` - добавлен метод `getProfile()` в `dictionaries`
- `src/store/useStore.ts` - обновлён метод `initialize()` для загрузки profile
- `src/pages/DashboardPage.tsx` - исправлено отображение лимита уроков
- `src/pages/ExercisePage.tsx` - исправлено отображение перевода пользователя

---

## Тестирование

### Тест 1: Лимит уроков на дашборде
1. Перейдите на страницу настроек
2. Измените "Уроков в день" на 10
3. Сохраните настройки
4. Вернитесь на дашборд
5. Проверьте, что отображается `X/10` вместо `X/5`

### Тест 2: Отображение перевода пользователя
1. Начните урок
2. Переведите предложение
3. Нажмите "Проверить"
4. Проверьте, что для каждого слова отображается блок "Ваш перевод: ..."

### Тест 3: Загрузка profile из backend
1. Откройте консоль браузера (F12)
2. Перезагрузите страницу
3. Проверьте логи:
```
🔑 initialize: User loaded: {...}
🔑 initialize: User is onboarded, loading profile...
🔑 initialize: Profile loaded: {user_id: 2, level: "A2", ...}
```

---

## Логирование

Добавлено подробное логирование для отладки:

### Backend
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

### Frontend
```
🔑 initialize: User loaded: {id: 2, email: "...", is_onboarded: true}
🔑 initialize: User is onboarded, loading profile...
🔑 initialize: Profile loaded: {user_id: 2, level: "A2", ...}

🏠 DashboardPage: Component mounted
🏠 DashboardPage: Current profile: {level: "A2", dailyLessonLimit: 10, ...}

💾 handleSave: Starting save process
💾 handleSave: Current state: {level: "B1", wordsPerLesson: 10, ...}
📝 handleSave: Sending to backend: {...}
✅ handleSave: Backend response: {status: "ok"}
🔄 handleSave: Updating profile in store: {...}
🔄 handleSave: Store updated, verifying: {...}

🔍 Word 0 rendering: {surface_form: "house", user_fragment: "дом", ...}
   user_fragment: дом
   userFragment: undefined
   Mapped userFragment: дом
   Has userFragment: true
```

---

## Дополнительные улучшения

### Автоматическая перезагрузка profile после сохранения настроек

Можно добавить автоматическую перезагрузку profile после сохранения настроек:

```typescript
const handleSave = async () => {
  try {
    await api.settings.update({...});
    
    // Перезагружаем profile из backend
    const profileData = await api.dictionaries.getProfile();
    useStore.setState({
      profile: {
        userId: String(profileData.user_id),
        level: profileData.level as any,
        dictionaryId: profileData.dictionary_id,
        dailyLessonLimit: profileData.daily_lesson_limit,
        wordsPerLesson: profileData.words_per_lesson,
        lastLessonNumber: profileData.last_lesson_number,
        userWords: [],
      }
    });
    
    navigate('/dashboard');
  } catch (err) {
    // ...
  }
};
```

Это гарантирует, что store содержит актуальные данные из базы данных после сохранения настроек.

---

## Связанные документы

- `docs/SETTINGS_PAGE.md` - документация страницы настроек
- `docs/FIX_SETTINGS_SAVE.md` - исправление проблемы сохранения настроек
- `docs/SETTINGS_DIAGNOSTICS.md` - диагностика проблем с настройками
- `docs/FIX_USER_TRANSLATION_DISPLAY.md` - отображение перевода пользователя
