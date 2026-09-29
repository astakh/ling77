# 📚 Импорт слов в словари

## 🎯 Обзор

Система импорта позволяет добавлять слова в словари из JSON-файла с автоматической проверкой дубликатов.

**Возможности:**
- ✅ Импорт из файла `words.json`
- ✅ Автоматическая проверка дубликатов
- ✅ Создание нового словаря или импорт в существующий
- ✅ Режим dry-run (предпросмотр без сохранения)
- ✅ Валидация формата данных
- ✅ Детальная статистика импорта

---

## 📋 Формат файла words.json

Файл должен содержать JSON-массив объектов:

```json
[
  {
    "lemma": "house",
    "pos": "noun",
    "level": "A1",
    "translations": ["дом", "жилище"]
  },
  {
    "lemma": "run",
    "pos": "verb",
    "level": "A1",
    "translations": ["бежать", "бегать"]
  },
  {
    "lemma": "beautiful",
    "pos": "adjective",
    "level": "A2",
    "translations": ["красивый", "прекрасный", "красивая"]
  }
]
```

### Обязательные поля

| Поле | Тип | Описание | Примеры |
|------|-----|----------|---------|
| `lemma` | string | Начальная форма слова | `"house"`, `"run"`, `"beautiful"` |
| `pos` | string | Часть речи | `"noun"`, `"verb"`, `"adjective"`, `"adverb"` |
| `level` | string | Уровень владения | `"A1"`, `"A2"`, `"B1"`, `"B2"` |
| `translations` | array | Массив русских переводов | `["дом", "жилище"]` |

### Правила валидации

- **lemma** — не пустая строка, начальная форма (единственное число для nouns, infinitive для verbs)
- **pos** — одно из: `noun`, `verb`, `adjective`, `adverb`
- **level** — одно из: `A1`, `A2`, `B1`, `B2`
- **translations** — массив строк, минимум 1 элемент
- **Уникальность** — комбинация `lemma + pos` должна быть уникальной в пределах словаря

---

## 🚀 Использование скрипта

### Базовый синтаксис

```bash
cd backend
python scripts/import_words.py [OPTIONS]
```

### Опции

| Опция | Описание | Пример |
|-------|----------|--------|
| `--dictionary-id ID` | ID существующего словаря | `--dictionary-id 1` |
| `--dictionary-name NAME` | Имя словаря (создаст если не существует) | `--dictionary-name "Словарь B1"` |
| `--file PATH` | Путь к файлу (по умолчанию: `words.json`) | `--file my_words.json` |
| `--dry-run` | Предпросмотр без сохранения | `--dry-run` |

### Примеры использования

#### Пример 1: Импорт в существующий словарь

```bash
cd backend
python scripts/import_words.py --dictionary-id 1
```

Вывод:
```
📖 Loading words from 'words.json'...
✅ Loaded 50 words

📥 Importing 50 words into dictionary 'Базовый словарь A1'...
  ✅ Added: house (noun) - дом, жилище
  ✅ Added: run (verb) - бежать, бегать
  ⏭️  Skipped: water (noun) - already exists
  ...

==================================================
📊 Import Summary
==================================================
  Total words in file: 50
  ✅ Created: 45
  ⏭️  Skipped (duplicates): 5
  ❌ Errors: 0
==================================================
```

#### Пример 2: Создание нового словаря

```bash
python scripts/import_words.py --dictionary-name "Бизнес-лексика B1"
```

Если словарь не существует, он будет создан автоматически.

#### Пример 3: Предпросмотр (dry-run)

```bash
python scripts/import_words.py --dictionary-id 1 --dry-run
```

Покажет, что будет импортировано, без сохранения в БД.

#### Пример 4: Импорт из другого файла

```bash
python scripts/import_words.py --dictionary-id 1 --file travel_words.json
```

---

## 🤖 Генерация слов через LLM

### Промпт для ChatGPT / Claude / GigaChat

```
Создай JSON-файл со списком английских слов для изучения.

ТРЕБОВАНИЯ:
- Формат: JSON-массив объектов
- Каждое слово должно содержать поля:
  * "lemma" - начальная форма слова (строка)
  * "pos" - часть речи: "noun", "verb", "adjective", "adverb" (строка)
  * "level" - уровень: "A1", "A2", "B1" или "B2" (строка)
  * "translations" - массив русских переводов (1-3 варианта)

- Количество слов: 50
- Уровень: A2
- Тематика: путешествия и транспорт

ФОРМАТ ВЫВОДА:
Только валидный JSON, без пояснений и markdown-разметки.
```

**Полный промпт и примеры:** см. `docs/LLM_PROMPT_FOR_WORDS.md`

### Процесс работы

1. **Сгенерируйте слова через LLM** используя промпт выше
2. **Сохраните результат** в файл `backend/words.json`
3. **Проверьте валидность JSON:**
   ```bash
   python -m json.tool words.json > /dev/null && echo "✅ Valid"
   ```
4. **Импортируйте в словарь:**
   ```bash
   python scripts/import_words.py --dictionary-name "Новый словарь"
   ```

---

## 🔍 Проверка дубликатов

Скрипт автоматически проверяет дубликаты по нормализованной комбинации `lemma + pos`:

```python
lemma_key = unicodedata.normalize("NFC", lemma).casefold().strip()
# Примеры:
# "House" → "house"
# "RUN" → "run"
# "  beautiful  " → "beautiful"
```

Если слово с таким `lemma_key + pos` уже есть в словаре, оно будет пропущено.

---

## 📊 Статистика импорта

После импорта выводится сводка:

```
==================================================
📊 Import Summary
==================================================
  Total words in file: 100
  ✅ Created: 85
  ⏭️  Skipped (duplicates): 10
  ❌ Errors: 5
==================================================
```

- **Total words in file** — общее количество слов в файле
- **Created** — успешно добавлено в БД
- **Skipped** — пропущено как дубликаты
- **Errors** — ошибки валидации или другие проблемы

---

## 🛠️ Решение проблем

### Ошибка: File 'words.json' not found

**Решение:** Убедитесь, что файл находится в папке `backend/` или укажите полный путь:
```bash
python scripts/import_words.py --file /path/to/words.json --dictionary-id 1
```

### Ошибка: Invalid JSON

**Решение:** Проверьте валидность JSON:
```bash
# Linux/Mac
python -m json.tool words.json > /dev/null

# Windows
Get-Content words.json | ConvertFrom-Json | Out-Null
```

### Ошибка: Dictionary with id=X not found

**Решение:** Посмотрите список доступных словарей:
```bash
python scripts/import_words.py --dictionary-id 999
```
Скрипт покажет все существующие словари с их ID.

### Ошибка: Must specify either --dictionary-id or --dictionary-name

**Решение:** Укажите либо ID существующего словаря, либо имя нового:
```bash
# Вариант 1: существующий словарь
python scripts/import_words.py --dictionary-id 1

# Вариант 2: новый словарь
python scripts/import_words.py --dictionary-name "Мой словарь"
```

### Ошибка: Item X missing required field

**Решение:** Проверьте структуру JSON. Каждое слово должно содержать все 4 поля:
```json
{
  "lemma": "word",
  "pos": "noun",
  "level": "A1",
  "translations": ["слово"]
}
```

---

## 💡 Советы

### 1. Всегда используйте dry-run сначала

```bash
python scripts/import_words.py --dictionary-id 1 --dry-run
```

Это покажет, что будет импортировано, без изменения БД.

### 2. Разбивайте большие файлы

Если у вас более 1000 слов, разбейте на несколько файлов и импортируйте по частям.

### 3. Проверяйте качество переводов

- Указывайте 2-3 варианта перевода для многозначных слов
- Первый перевод должен быть самым частотным
- Избегайте разговорных вариантов для учебных слов

### 4. Группируйте по темам

Создавайте отдельные словари для разных тематик:
- "Базовый A1"
- "Путешествия A2"
- "Бизнес B1"
- "Академический B2"

### 5. Используйте LLM для генерации

Промпт для LLM значительно ускоряет создание словарей. См. `docs/LLM_PROMPT_FOR_WORDS.md`

---

## 📝 Пример полного workflow

```bash
# 1. Перейти в папку backend
cd backend

# 2. Создать файл words.json (вручную или через LLM)
# ... содержимое файла ...

# 3. Проверить валидность
python -m json.tool words.json > /dev/null && echo "✅ Valid JSON"

# 4. Предпросмотр импорта
python scripts/import_words.py --dictionary-name "Новый словарь B1" --dry-run

# 5. Если всё ок — импортировать
python scripts/import_words.py --dictionary-name "Новый словарь B1"

# 6. Проверить результат в БД
psql -h your-server -U wordflow_user -d wordflow -c "SELECT COUNT(*) FROM words WHERE dictionary_id = (SELECT id FROM dictionaries WHERE name = 'Новый словарь B1');"
```

---

## 🔗 Связанные документы

- `docs/LLM_PROMPT_FOR_WORDS.md` — промпты для генерации слов через LLM
- `docs/DATABASE_SETUP.md` — настройка базы данных
- `docs/FULL_STACK_LAUNCH.md` — запуск полного стека

---

## 📂 Структура файлов

```
backend/
├── scripts/
│   ├── import_words.py      # Скрипт импорта
│   └── seed.py              # Начальное наполнение БД
├── words.json               # Файл для импорта (в .gitignore)
├── words.example.json       # Пример формата
└── ...
```

**Важно:** `words.json` добавлен в `.gitignore` и не коммитится в репозиторий.
