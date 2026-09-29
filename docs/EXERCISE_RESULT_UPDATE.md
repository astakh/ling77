# 📝 Обновление страницы результата упражнения

## Что добавлено

На странице результата проверки перевода добавлены два новых блока:

### 1. Блок оценки целевых слов

Показывает детальную информацию по каждому целевому слову:

**Для правильных переводов:**
- ✓ Зелёная галочка
- Слово
- "✓ Правильно"

**Для опечаток:**
- ⚠ Жёлтый предупреждающий знак
- Слово
- "⚠ Опечатка"
- "Ваш перевод: ..."

**Для неправильных переводов:**
- ✗ Красный крестик
- Слово
- "✗ Неправильно"
- "Ваш перевод: ..." (если есть)
- "Правильный перевод: ..."

### 2. Блок добавления новых слов в словарь

Показывает слова, которые ученик пропустил или перевёл неправильно:

- Список слов с чекбоксами
- Можно выбрать какие слова добавить
- Кнопка "Добавить выбранные слова (N)"
- Счётчик выбранных слов

## Как это работает

### Данные

Backend возвращает в `resultData`:
- `words` - массив целевых слов с оценкой
- `newSuggestedWords` - массив новых слов для добавления

Каждое слово в `words` содержит:
- `wordId` - ID слова
- `surfaceForm` - форма слова
- `result` - результат оценки (correct/typo/incorrect/dont_know)
- `userFragment` - как ученик перевёл это слово

### Состояние

```typescript
const [selectedNewWords, setSelectedNewWords] = useState<Set<string>>(new Set());
```

Хранит выбранные слова для добавления в словарь.

### Функции

**handleToggleWord(word)**
- Добавляет/удаляет слово из выбранных
- Обновляет чекбоксы

**handleAddSelectedWords()**
- TODO: Реализовать API вызов для добавления слов в словарь
- Показывает alert с количеством добавленных слов
- Очищает выбор

## Визуальное оформление

### Блок оценки слов

```
┌─────────────────────────────────────────┐
│ 📝 ОЦЕНКА СЛОВ                          │
│                                         │
│ ✓ house                                 │
│   ✓ Правильно                           │
│                                         │
│ ⚠ beautiful                             │
│   ⚠ Опечатка                            │
│   Ваш перевод: красивый                 │
│                                         │
│ ✗ important                             │
│   ✗ Неправильно                         │
│   Ваш перевод: важный                   │
│   Правильный перевод: важный            │
└─────────────────────────────────────────┘
```

### Блок добавления слов

```
┌─────────────────────────────────────────┐
│ 💡 ДОБАВИТЬ В СЛОВАРЬ                   │
│                                         │
│ Эти слова встретились в предложении,    │
│ но вы их не перевели. Выберите слова    │
│ для добавления в словарь:               │
│                                         │
│ ☑ word1                                 │
│ ☐ word2                                 │
│ ☑ word3                                 │
│                                         │
│ [Добавить выбранные слова (2)]          │
└─────────────────────────────────────────┘
```

## Следующие шаги

### Реализовать добавление слов в словарь

Сейчас функция `handleAddSelectedWords()` только показывает alert. Нужно:

1. Создать API endpoint в backend:
   ```python
   POST /vocabulary/add-words
   {
     "words": ["word1", "word2", "word3"]
   }
   ```

2. Backend должен:
   - Найти слова в таблице `words` по lemma
   - Создать записи в `user_words` для каждого слова
   - Установить stage=0, status='active'

3. Frontend должен:
   - Вызвать API
   - Показать успех/ошибку
   - Обновить UI

### Пример реализации

**Backend (`backend/routes/vocabulary.py`):**
```python
@router.post("/add-words")
async def add_words_to_vocabulary(
    body: AddWordsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get user's learning profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    added = []
    for word_lemma in body.words:
        # Find word in dictionary
        result = await db.execute(
            select(Word).where(Word.lemma == word_lemma)
        )
        word = result.scalar_one_or_none()
        
        if word:
            # Check if already in user's vocabulary
            result = await db.execute(
                select(UserWord).where(
                    UserWord.learning_profile_id == profile.id,
                    UserWord.word_id == word.id,
                )
            )
            if not result.scalar_one_or_none():
                # Add to vocabulary
                user_word = UserWord(
                    learning_profile_id=profile.id,
                    word_id=word.id,
                    status='active',
                    stage=0,
                    due_lesson_number=profile.last_lesson_number + 1,
                )
                db.add(user_word)
                added.append(word_lemma)
    
    await db.flush()
    
    return {"added": added, "count": len(added)}
```

**Frontend (`src/api/client.ts`):**
```typescript
vocabulary: {
  // ... existing methods
  
  addWords: (words: string[]) =>
    request<{ added: string[]; count: number }>('/vocabulary/add-words', {
      method: 'POST',
      body: JSON.stringify({ words }),
    }),
}
```

**Frontend (`src/pages/ExercisePage.tsx`):**
```typescript
const handleAddSelectedWords = async () => {
  if (selectedNewWords.size === 0) return;
  
  try {
    const response = await api.vocabulary.addWords(Array.from(selectedNewWords));
    alert(`Добавлено слов: ${response.count}`);
    setSelectedNewWords(new Set());
  } catch (error) {
    console.error('Failed to add words:', error);
    alert('Не удалось добавить слова в словарь');
  }
};
```

## Файлы изменённые

- `src/pages/ExercisePage.tsx` - добавлены блоки оценки слов и добавления новых слов

## Тестирование

1. Перезапустите frontend:
   ```bash
   npm run dev
   ```

2. Начните урок и переведите предложение

3. После проверки должны увидеть:
   - Блок "📝 Оценка слов" с деталями по каждому слову
   - Блок "💡 Добавить в словарь" с чекбоксами (если есть новые слова)

4. Выберите слова и нажмите "Добавить выбранные слова"

5. Должен появиться alert с количеством добавленных слов

## Итог

✅ Добавлен блок оценки целевых слов с деталями  
✅ Добавлен блок выбора новых слов для добавления в словарь  
✅ Реализована логика выбора слов (чекбоксы)  
✅ Добавлена кнопка добавления с счётчиком  
✅ Проект успешно собран  

Следующий шаг: реализовать backend API для добавления слов в словарь.
