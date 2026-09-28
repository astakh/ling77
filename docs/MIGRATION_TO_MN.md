# 🔄 Миграция на новую структуру словарей

## ⚠️ Важно!

Структура БД изменена для поддержки M:N связи между словарями и словами. 
Если у вас уже есть данные в БД, нужно пересоздать базу.

---

## 📋 Что изменилось

### Старая структура (1:N)
```
Dictionary 1:N Word
(слово принадлежит только одному словарю)
```

### Новая структура (M:N)
```
Dictionary M:N Word через DictionaryWord
(слово может быть в нескольких словарях)
```

### Новая таблица `dictionaries`
Добавлены поля:
- `category` — категория словаря (general, it, travel, business, food, medical)
- `is_active` — активен ли словарь

---

## 🚀 Инструкция по миграции

### Шаг 1. Остановить backend

```bash
# В терминале с backend нажмите Ctrl+C
```

### Шаг 2. Удалить старую БД

Подключитесь к PostgreSQL на сервере:

```bash
psql -h your-server-ip -U postgres
```

Выполните SQL:

```sql
-- Удалить старую БД
DROP DATABASE IF EXISTS wordflow;

-- Создать новую
CREATE DATABASE wordflow
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Выдать права
\c wordflow
GRANT ALL ON SCHEMA public TO wordflow_user;
ALTER DATABASE wordflow OWNER TO wordflow_user;

\q
```

### Шаг 3. Применить миграции

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
alembic upgrade head
```

### Шаг 4. Заполнить словари

```bash
python scripts/seed.py
```

Ожидается вывод:
```
Creating dictionaries...
  + Created dictionary 'Базовый словарь A1' (id=1, category=general)
  + Created dictionary 'Элементарный словарь A2' (id=2, category=general)
  ...
  + Created dictionary 'IT и технологии' (id=6, category=it)
  + Created dictionary 'Путешествия' (id=7, category=travel)
  ...

Adding words to dictionaries...
  ✅ Added: house (noun) - дом, жилище
  ...

Adding thematic words...
  ✅ Added: algorithm (noun) - алгоритм
  ...

=== Summary ===
  Базовый словарь A1 [general]: 20 words
  Элементарный словарь A2 [general]: 20 words
  ...
  IT и технологии [it]: 10 words
  Путешествия [travel]: 10 words
  ...
```

### Шаг 5. Запустить backend

```bash
uvicorn main:app --reload
```

---

## ✅ Проверка

Подключитесь к БД и проверьте структуру:

```bash
psql -h your-server-ip -U wordflow_user -d wordflow
```

```sql
-- Проверить таблицы
\dt

-- Должны быть:
-- dictionaries
-- words
-- dictionary_words  <-- НОВАЯ!
-- learning_profiles
-- user_words
-- lessons
-- ...

-- Проверить словари
SELECT id, name, category FROM dictionaries;

-- Должны быть:
-- 1 | Базовый словарь A1       | general
-- 2 | Элементарный словарь A2  | general
-- ...
-- 6 | IT и технологии          | it
-- 7 | Путешествия              | travel
-- 8 | Бизнес и работа          | business
-- 9 | Еда и рестораны          | food
-- 10| Медицина и здоровье      | medical

-- Проверить M:N связь
SELECT d.name, COUNT(dw.word_id) as word_count
FROM dictionaries d
LEFT JOIN dictionary_words dw ON d.id = dw.dictionary_id
GROUP BY d.id, d.name
ORDER BY d.id;

-- Проверить, что слово может быть в нескольких словарях
SELECT w.lemma, COUNT(dw.dictionary_id) as dict_count
FROM words w
JOIN dictionary_words dw ON w.id = dw.word_id
GROUP BY w.id, w.lemma
HAVING COUNT(dw.dictionary_id) > 1
LIMIT 5;

\q
```

---

## 🎯 Новые возможности

### 1. Тематические словари
Пользователь может выбрать словарь по теме:
- IT и технологии
- Путешествия
- Бизнес и работа
- Еда и рестораны
- Медицина и здоровье

### 2. Слово в нескольких словарях
Одно и то же слово (например, "contract") может быть:
- В общем словаре B1
- В словаре "Бизнес и работа"
- В словаре "Путешествия" (если уместно)

### 3. Категории словарей
Каждый словарь имеет категорию для фильтрации и группировки.

---

## 🆘 Если что-то пошло не так

### Ошибка: relation "dictionary_words" does not exist
```bash
alembic upgrade head
```

### Ошибка: duplicate key value violates unique constraint
Удалите дубликаты из `words.json` и повторите импорт.

### Словари не создались
Проверьте, что `seed.py` запущен из папки `backend/`.

---

## 📚 Документация

- Полная инструкция по импорту: `docs/IMPORT_WORDS.md`
- Промпты для LLM: `docs/LLM_PROMPT_FOR_WORDS.md`
- Настройка БД: `docs/DATABASE_SETUP.md`
