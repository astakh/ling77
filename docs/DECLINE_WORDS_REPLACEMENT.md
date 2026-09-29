# 📚 Функция замены отклоненных слов

## 🎯 Что реализовано

Теперь при отклонении слова на странице "Состав урока" оно **автоматически заменяется** другим словом из словаря, чтобы сохранить нужное количество слов в уроке.

## 🔄 Как это работает

### Frontend (React)

1. **Страница превью урока** (`LessonPreviewPage.tsx`):
   - При нажатии на ✕ рядом со словом вызывается `handleDecline(wordId)`
   - Слово добавляется в список `declinedWords` через `declineWord(wordId)`
   - **Автоматически** вызывается `loadPreview()` для обновления списка

2. **Store** (`useStore.ts`):
   - `previewLesson()` передает `declinedWords` в backend API
   - `startLesson()` также передает `declinedWords` чтобы они не попали в урок

3. **API Client** (`client.ts`):
   - `api.lesson.preview(declinedWordIds)` - отправляет POST запрос с массивом ID отклоненных слов
   - `api.lesson.start(declinedWordIds)` - отправляет POST запрос с массивом ID отклоненных слов

### Backend (FastAPI)

1. **Схемы** (`schemas.py`):
   ```python
   class LessonPreviewRequest(BaseModel):
       declined_word_ids: list[int] = []
   
   class LessonStartRequest(BaseModel):
       declined_word_ids: list[int] = []
   ```

2. **Endpoints** (`routes/lesson.py`):
   - `POST /lesson/preview` - принимает `declined_word_ids` и передает в `select_words_for_lesson()`
   - `POST /lesson/start` - принимает `declined_word_ids` и передает в `select_words_for_lesson()`

3. **Логика подбора слов** (`select_words_for_lesson()`):
   - Уже поддерживала параметр `declined_word_ids`
   - Исключает отклоненные слова из выборки
   - Подбирает замены из доступных слов того же уровня

## 📊 Пример работы

### Сценарий:
1. Пользователь открывает страницу "Состав урока"
2. Backend возвращает 8 слов: `[house, water, food, book, friend, school, work, time]`
3. Пользователь отклоняет слово `food` (ID=3)
4. Frontend отправляет POST `/lesson/preview` с `declined_word_ids: [3]`
5. Backend исключает `food` и подбирает замену, например `friend` (если она еще не в списке)
6. Frontend обновляет список: `[house, water, book, friend, school, work, time, new_word]`

## 🔧 Технические детали

### API Endpoints

#### POST /lesson/preview
```json
// Request
{
  "declined_word_ids": [3, 7, 12]
}

// Response
{
  "words": [
    {
      "id": 1,
      "lemma": "house",
      "translations": ["дом", "жилище"],
      "is_new": true,
      "is_due": false
    }
    // ... другие слова (без отклоненных)
  ]
}
```

#### POST /lesson/start
```json
// Request
{
  "declined_word_ids": [3, 7, 12]
}

// Response
{
  "lesson_id": 42,
  "lesson_number": 5,
  "exercises": [...]
}
```

### Логика подбора слов

Функция `select_words_for_lesson()` в `backend/routes/lesson.py`:

```python
async def select_words_for_lesson(
    db: AsyncSession,
    profile: LearningProfile,
    declined_word_ids: set[int] | None = None,
) -> tuple[list[dict], list[dict]]:
    """
    Подбирает слова для урока:
    1. Due words (слова на повторение) - до 5 штук
    2. New words (новые слова) - до 3 штук
    
    Исключает слова из declined_word_ids
    """
    declined = declined_word_ids or set()
    
    # Получаем due words (исключая отклоненные)
    due_words = [...]  # слова которые нужно повторить
    due_words = [w for w in due_words if w.word_id not in declined]
    
    # Получаем new words (исключая отклоненные)
    new_words = [...]  # новые слова из словаря
    new_words = [w for w in new_words if w.word_id not in declined]
    
    return due_words[:5], new_words[:3]
```

## 🎨 UI/UX

### Страница превью урока

- При нажатии ✕ слово **мгновенно** исчезает из списка
- На его месте появляется другое слово (загрузка занимает ~200-500мс)
- Счетчик слов остается неизменным (например, "В этом уроке 8 слов")
- Если слов для замены не осталось, показывается сообщение "Нет слов для урока"

### Сброс отклоненных слов

Если пользователь отклонил слишком много слов и replacements закончились:
- Показывается кнопка "Сбросить отклонённые слова"
- При нажатии очищается `declinedWords` в store
- Пользователь перенаправляется на dashboard

## 🧪 Тестирование

### Ручное тестирование:

1. Зарегистрируйтесь и пройдите онбординг
2. На dashboard нажмите "Начать урок"
3. На странице "Состав урока" отклоните несколько слов (нажмите ✕)
4. Убедитесь что:
   - Отклоненные слова исчезают
   - Появляются новые слова взамен
   - Общее количество слов не меняется
5. Нажмите "Начать урок"
6. Убедитесь что отклоненные слова не попали в урок

### Автоматическое тестирование:

```bash
# Backend тесты (если есть)
cd backend
pytest tests/test_lesson.py -v

# Frontend тесты (если есть)
npm test
```

## 🐛 Известные ограничения

1. **Конечный пул слов**: если пользователь отклонит все доступные слова, replacements закончатся
2. **Уровень пользователя**: замены подбираются только из слов соответствующего уровня
3. **Словарь**: замены подбираются только из выбранного словаря

## 🚀 Будущие улучшения

1. **Кэширование**: кэшировать превью на frontend чтобы уменьшить нагрузку на backend
2. **Анимация**: добавить плавную анимацию замены слов
3. **Undo**: добавить возможность отменить отклонение слова
4. **Приоритеты**: учитывать приоритет слов (например, более частотные слова важнее)
5. **Статистика**: показывать сколько слов было отклонено в этом уроке

## 📝 Связанные файлы

### Frontend:
- `src/pages/LessonPreviewPage.tsx` - страница превью урока
- `src/store/useStore.ts` - Zustand store
- `src/api/client.ts` - API клиент

### Backend:
- `backend/routes/lesson.py` - endpoints для уроков
- `backend/schemas.py` - Pydantic схемы
- `backend/models.py` - SQLAlchemy модели

## 🔗 Связанные документы

- [Архитектура словарей](./DICTIONARY_ARCHITECTURE.md)
- [Импорт слов](./IMPORT_WORDS.md)
- [Полный запуск](./FULL_STACK_LAUNCH.md)
