# 🔍 Подробное логирование LLM вызовов

## Проблема

При ошибке 503 (Service Unavailable) было сложно понять что именно пошло не так - недостаточно информации в логах.

## Решение

Добавлено детальное логирование на всех этапах работы с LLM:

### 1. Оценка перевода (`backend/routes/lesson.py`)

При ошибке теперь логируется:
- Тип ошибки
- ID упражнения
- Целевое предложение
- Перевод пользователя
- Целевые слова
- Полный traceback

```python
logger.error(f"❌ LLM evaluation failed: {e}")
logger.error(f"   Error type: {type(e).__name__}")
logger.error(f"   Exercise ID: {exercise.id}")
logger.error(f"   Target sentence: {exercise.target_sentence}")
logger.error(f"   User translation: {body.user_translation}")
logger.error(f"   Target words: {target_words_data}")
logger.error(f"   Traceback:\n{traceback.format_exc()}")
```

### 2. Вызов LLM (`backend/llm_client.py`)

#### evaluate_translation()

Логируется:
- Запрос на оценку (предложение, перевод, целевые слова)
- Каждая попытка (attempt 1/2, 2/2)
- Сырой ответ от LLM
- Результат валидации
- Полный traceback при ошибке

```python
logger.info(f"🔍 Evaluate translation request:")
logger.info(f"   Target sentence: {target_sentence}")
logger.info(f"   User translation: {user_translation}")
logger.info(f"   Target words: {[w['lemma'] for w in target_words]}")
logger.info(f"   Prompt length: {len(prompt)} chars")

logger.info(f"🔄 Evaluate attempt {attempt + 1}/2")
logger.info(f"📥 LLM raw response: {result}")
```

#### _validate_evaluate_response()

Логируется каждая проверка:
- Тип результата
- Наличие обязательных ключей
- Значения полей
- Причина ошибки валидации

```python
logger.info(f"🔍 Validating LLM response...")
logger.warning(f"   ❌ Missing 'evaluations' key. Keys: {result.keys()}")
logger.warning(f"   ❌ Invalid overall_result: {result['overall_result']}")
logger.info(f"   ✅ Validation passed")
```

#### _call_llm()

Логируется:
- Каждая попытка вызова API
- Тип и сообщение ошибки
- Полный traceback
- Сырой контент от LLM (первые 500 символов)
- Результат парсинга JSON

```python
logger.error(f"❌ GigaChat call failed (attempt {attempt + 1}): {e}")
logger.error(f"   Error type: {type(e).__name__}")
logger.error(f"   Full traceback:\n{traceback.format_exc()}")

logger.info(f"📝 Raw content from LLM:\n{content[:500]}...")
logger.error(f"❌ Failed to parse JSON: {e}")
logger.error(f"   Content that failed to parse:\n{content}")
```

## Примеры логов

### Успешный вызов

```
🔍 Evaluate translation request:
   Target sentence: The house is big
   User translation: Дом большой
   Target words: ['house', 'big']
   Prompt length: 456 chars
🔄 Evaluate attempt 1/2
🤖 Calling GigaChat API (attempt 1/3)
   Purpose: evaluate_translation
   Temperature: 0.2
📊 Response received
   Response type: ChatCompletion
   Content length: 234 chars
   Tokens: 150
✅ GigaChat response received
   Latency: 2500ms
📝 Raw content from LLM:
{"evaluations": [{"word_lemma": "house", "result": "correct", ...}]}
✅ JSON parsed successfully
   Result type: dict
   Result keys: dict_keys(['evaluations', 'overall_result', 'new_suggested_words'])
📥 LLM raw response: {'evaluations': [...], 'overall_result': 'correct', ...}
🔍 Validating LLM response...
   ✅ Validation passed
✅ Response validated successfully
✅ Translation evaluated using GigaChat LLM
📊 LLM Response:
   Overall result: correct
   Evaluations: [...]
   New suggested words: []
```

### Ошибка парсинга JSON

```
📝 Raw content from LLM:
I cannot help with that request...
❌ Failed to parse JSON: Expecting value: line 1 column 1 (char 0)
   Content that failed to parse:
I cannot help with that request...
❌ GigaChat call failed (attempt 1): Expecting value: line 1 column 1 (char 0)
   Error type: JSONDecodeError
   Full traceback:
Traceback (most recent call last):
  File "backend/llm_client.py", line 142, in _call_llm
    result = self._parse_json_response(content)
  ...
```

### Ошибка валидации

```
📥 LLM raw response: {'evaluations': [...], 'overall_result': 'correct'}
🔍 Validating LLM response...
   ❌ Missing 'new_suggested_words' key. Keys: dict_keys(['evaluations', 'overall_result'])
❌ Response validation failed
   Response type: dict
   Response keys: dict_keys(['evaluations', 'overall_result'])
   Full response: {'evaluations': [...], 'overall_result': 'correct'}
```

### Ошибка API

```
❌ GigaChat call failed (attempt 1): Connection timeout
   Error type: TimeoutError
   Error message: Connection timeout
   Full traceback:
Traceback (most recent call last):
  File "backend/llm_client.py", line 102, in _call_llm
    response = giga.chat(...)
  ...
   Retrying in 1 second...
```

## Как использовать

### 1. Перезапустите backend

```bash
cd backend
uvicorn main:app --reload
```

### 2. Выполните действие

Переведите предложение в упражнении.

### 3. Проверьте логи

В терминале backend увидите детальную информацию:
- Что было отправлено в LLM
- Что вернул LLM
- Где произошла ошибка (если есть)
- Полный traceback

### 4. Анализ ошибок

#### Ошибка 503 с "Failed to parse JSON"

**Причина:** LLM вернул не JSON, а текст

**Решение:**
- Проверьте промпт в `backend/prompts/evaluate_translation.txt`
- Убедитесь что промпт явно требует JSON формат
- Проверьте что модель GigaChat-3-Ultra доступна

#### Ошибка 503 с "Missing 'new_suggested_words' key"

**Причина:** LLM вернул JSON, но без обязательного поля

**Решение:**
- Проверьте промпт - явно укажите что нужно поле `new_suggested_words`
- Или сделайте поле опциональным в валидации

#### Ошибка 503 с "Connection timeout"

**Причина:** Проблема с сетью или GigaChat API недоступен

**Решение:**
- Проверьте интернет-соединение
- Проверьте статус GigaChat API
- Увеличьте таймауты в настройках

## Настройка уровня логирования

По умолчанию логируется всё (INFO, WARNING, ERROR).

Для отключения подробных логов измените в `backend/main.py`:

```python
logging.basicConfig(
    level=logging.WARNING,  # или logging.ERROR
    ...
)
```

## Мониторинг

Для продакшена рекомендуется:
1. Настроить сбор логов в файл
2. Использовать систему мониторинга (Sentry, LogRocket)
3. Настроить алерты на частые ошибки

## Файлы изменённые

- `backend/routes/lesson.py` - логирование ошибок оценки
- `backend/llm_client.py` - логирование вызовов LLM, валидации, парсинга

## Итог

✅ Добавлено подробное логирование на всех этапах  
✅ Логируется полный traceback при ошибках  
✅ Видно что отправляется в LLM и что возвращается  
✅ Видно где именно происходит ошибка  
✅ Легко диагностировать проблемы  

Теперь при ошибке 503 вы точно увидите что пошло не так! 🔍
