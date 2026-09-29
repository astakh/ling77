# 📚 Импорт слов в словари — Краткое руководство

## 🎯 Быстрый старт

### 1. Создайте файл `words.json` в папке `backend/`

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
  }
]
```

### 2. Импортируйте слова

```bash
cd backend
python scripts/import_words.py --dictionary-name "Мой словарь"
```

**Готово!** ✨

---

## 🤖 Генерация слов через LLM

Используйте этот промпт для ChatGPT / Claude / GigaChat:

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
- Уровень: A1
- Тематика: базовые повседневные слова

ФОРМАТ ВЫВОДА:
Только валидный JSON, без пояснений и markdown-разметки.
```

**Подробнее:** `docs/LLM_PROMPT_FOR_WORDS.md`

---

## 📋 Команды

### Импорт в существующий словарь
```bash
python scripts/import_words.py --dictionary-id 1
```

### Создание нового словаря
```bash
python scripts/import_words.py --dictionary-name "Новый словарь B1"
```

### Предпросмотр (без сохранения)
```bash
python scripts/import_words.py --dictionary-id 1 --dry-run
```

### Импорт из другого файла
```bash
python scripts/import_words.py --dictionary-id 1 --file my_words.json
```

---

## 📊 Формат данных

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `lemma` | string | Начальная форма | `"house"` |
| `pos` | string | Часть речи | `"noun"`, `"verb"`, `"adjective"`, `"adverb"` |
| `level` | string | Уровень | `"A1"`, `"A2"`, `"B1"`, `"B2"` |
| `translations` | array | Русские переводы | `["дом", "жилище"]` |

---

## 🔍 Проверка дубликатов

Скрипт автоматически проверяет дубликаты по `lemma + pos`:
- Если слово уже есть в словаре → будет пропущено
- Нормализация: `"House"` = `"house"`, `"RUN"` = `"run"`

---

## 📖 Документация

- **Полное руководство:** `docs/IMPORT_WORDS.md`
- **Промпты для LLM:** `docs/LLM_PROMPT_FOR_WORDS.md`
- **Пример файла:** `backend/words.example.json`

---

## 💡 Советы

1. **Всегда используйте `--dry-run`** для предпросмотра перед импортом
2. **Разбивайте большие файлы** на части (макс. 1000 слов за раз)
3. **Указывайте 2-3 перевода** для многозначных слов
4. **Группируйте по темам** — создавайте отдельные словари

---

## 🆘 Частые проблемы

**Ошибка: File 'words.json' not found**
→ Убедитесь, что файл в папке `backend/` или укажите путь: `--file /path/to/file.json`

**Ошибка: Invalid JSON**
→ Проверьте валидность: `python -m json.tool words.json`

**Ошибка: Dictionary with id=X not found**
→ Посмотрите список словарей: `python scripts/import_words.py --dictionary-id 999`

---

**Готово!** 🎉 Слова импортированы и доступны в приложении.
