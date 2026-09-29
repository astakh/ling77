# Исправление проблемы сохранения настроек

## Проблема
После нажатия кнопки "Сохранить настройки" изменения не сохранялись в базу данных.

## Причина
В бэкенде использовался `await db.flush()` вместо `await db.commit()`. 

- `flush()` - отправляет изменения в базу данных, но не фиксирует транзакцию
- `commit()` - фиксирует транзакцию и делает изменения постоянными

Без `commit()` изменения откатывались после завершения запроса.

## Решение

### 1. Backend (`backend/routes/settings.py`)

**Было:**
```python
await db.flush()
return {"status": "ok"}
```

**Стало:**
```python
await db.commit()
return {"status": "ok"}
```

Также добавлено подробное логирование:
```python
logger.info(f"📝 Updating settings for user {user.id}")
logger.info(f"   Request body: level={body.level}, ...")
logger.info(f"   Current profile: level={profile.level}, ...")
logger.info(f"   ✓ Updated level to {body.level}")
logger.info(f"✅ Settings saved successfully for user {user.id}")
logger.info(f"   New profile: level={profile.level}, ...")
```

### 2. Frontend (`src/pages/SettingsPage.tsx`)

Добавлено логирование для отладки:
```typescript
console.log('📝 Saving settings:', { level, words_per_lesson, ... });
console.log('✅ Settings saved:', response);
console.log('🔄 Updating profile in store:', updatedProfile);
```

## Проверка

### 1. Перезапустите backend
```bash
cd backend
uvicorn main:app --reload
```

### 2. Перезапустите frontend
```bash
npm run dev
```

### 3. Проверьте сохранение настроек

1. Откройте http://localhost:3000
2. Войдите в систему
3. Перейдите на страницу настроек (иконка ⚙️)
4. Измените настройки:
   - Уровень: B1
   - Слов в уроке: 10
   - Уроков в день: 3
   - Словарь: IT и технологии
5. Нажмите "Сохранить настройки"

### 4. Проверьте логи

**В консоли браузера (F12):**
```
📝 Saving settings: {level: "B1", words_per_lesson: 10, lessons_per_day: 3, dictionary_id: 2}
✅ Settings saved: {status: "ok"}
🔄 Updating profile in store: {level: "B1", wordsPerLesson: 10, dailyLessonLimit: 3, dictionaryId: 2}
```

**В терминале backend:**
```
📝 Updating settings for user 2
   Request body: level=B1, words_per_lesson=10, lessons_per_day=3, dictionary_id=2
   Current profile: level=A1, words_per_lesson=8, daily_lesson_limit=5, dictionary_id=1
   ✓ Updated dictionary_id to 2
   ✓ Updated level to B1
   ✓ Updated words_per_lesson to 10
   ✓ Updated daily_lesson_limit to 3
✅ Settings saved successfully for user 2
   New profile: level=B1, words_per_lesson=10, daily_lesson_limit=3, dictionary_id=2
```

### 5. Проверьте базу данных

```sql
SELECT level, words_per_lesson, daily_lesson_limit, dictionary_id 
FROM learning_profiles 
WHERE user_id = 2;
```

Должно показать обновлённые значения:
```
 level | words_per_lesson | daily_lesson_limit | dictionary_id 
-------+------------------+--------------------+---------------
 B1    |               10 |                  3 |             2
```

### 6. Проверьте возврат на дашборд

После сохранения настроек должен произойти автоматический возврат на дашборд через 1 секунду.

## Изменённые файлы

- `backend/routes/settings.py` - заменён `flush()` на `commit()`, добавлено логирование
- `src/pages/SettingsPage.tsx` - добавлено логирование

## Дополнительные улучшения

### Валидация на фронтенде

Можно добавить проверку перед отправкой:

```typescript
const handleSave = async () => {
  // Валидация
  if (!dictionaryId) {
    setError('Выберите словарь');
    return;
  }
  
  if (wordsPerLesson < 3 || wordsPerLesson > 15) {
    setError('Количество слов в уроке должно быть от 3 до 15');
    return;
  }
  
  if (lessonsPerDay < 1 || lessonsPerDay > 10) {
    setError('Количество уроков в день должно быть от 1 до 10');
    return;
  }
  
  // ... остальной код
};
```

### Перезагрузка профиля с бэкенда

Вместо обновления store вручную, можно перезагрузить профиль:

```typescript
const handleSave = async () => {
  try {
    await api.settings.update({ ... });
    
    // Перезагружаем профиль с бэкенда
    const updatedProfile = await api.profile.get();
    useStore.setState({ profile: updatedProfile });
    
    navigate('/dashboard');
  } catch (err) {
    // ...
  }
};
```

Это гарантирует, что store содержит актуальные данные из базы.

## Тестирование различных сценариев

### Сценарий 1: Изменение только уровня
1. Измените только уровень (A1 → B2)
2. Сохраните
3. Проверьте, что другие настройки не изменились

### Сценарий 2: Изменение только словаря
1. Измените только словарь
2. Сохраните
3. Проверьте, что уровень и лимиты не изменились

### Сценарий 3: Изменение всех настроек
1. Измените все настройки
2. Сохраните
3. Проверьте, что все изменения сохранены

### Сценарий 4: Отмена сохранения
1. Измените настройки
2. Не нажимайте "Сохранить"
3. Перейдите на другую страницу
4. Вернитесь на страницу настроек
5. Проверьте, что настройки не изменились

## Ожидаемое поведение

✅ Настройки сохраняются в базу данных  
✅ Store обновляется после сохранения  
✅ Автоматический возврат на дашборд  
✅ Подробное логирование для отладки  
✅ Валидация данных на бэкенде  
✅ Обработка ошибок на фронтенде  

## Связанные документы

- `docs/SETTINGS_PAGE.md` - документация страницы настроек
- `SETTINGS_QUICKSTART.md` - краткая инструкция
