# 🔧 Обработка ошибок LLM (GigaChat)

## 📋 Проблема

При запуске урока backend пытается вызвать GigaChat API для генерации упражнений и оценки переводов. Если:
- Не настроены credentials в `.env`
- API недоступен
- Неправильный формат запроса
- Превышены лимиты

Backend возвращает ошибку **503 Service Unavailable**.

## ✅ Решение

При ошибке LLM backend возвращает ошибку 503 с сообщением "Сервис временно недоступен. Попробуйте позже." Frontend показывает это сообщение пользователю через `alert()`.

**Важно:** Fallback механизм **не реализован**. Если GigaChat недоступен, урок не может быть начат.

## 🔄 Как это работает

### Backend (FastAPI)

**Генерация упражнений (POST /lesson/start):**
```python
try:
    llm_results = await gigachat_client.generate_exercises(...)
    logger.info(f"✅ Generated {len(llm_results)} exercises using GigaChat LLM")
except Exception as e:
    logger.error(f"LLM generation failed: {e}")
    raise HTTPException(status_code=503, detail="Сервис временно недоступен. Попробуйте позже.")
```

**Оценка переводов (POST /lesson/evaluate):**
```python
try:
    llm_result = await gigachat_client.evaluate_translation(...)
    logger.info(f"✅ Translation evaluated using GigaChat LLM")
except Exception as e:
    logger.error(f"LLM evaluation failed: {e}")
    raise HTTPException(status_code=503, detail="Сервис временно недоступен. Попробуйте позже.")
```

### Frontend (React)

**При начале урока (LessonPreviewPage.tsx):**
```typescript
try {
  await startLesson();
  navigate('/lesson/exercise');
} catch (error: any) {
  if (error.status === 503) {
    alert('Сервис временно недоступен. Попробуйте позже.');
  } else {
    alert(`Ошибка: ${error.detail || 'Не удалось начать урок'}`);
  }
}
```

**При оценке перевода (ExercisePage.tsx):**
```typescript
try {
  const result = await evaluateExercise(parseInt(exercise.id), exerciseDraft);
  // ...
} catch (error: any) {
  if (error.status === 503) {
    alert('Сервис временно недоступен. Попробуйте позже. Ваш перевод сохранён.');
  } else {
    alert(`Ошибка: ${error.detail || 'Не удалось проверить перевод'}`);
  }
}
```

## 📊 Логи

### При успешном использовании GigaChat:
```
✅ Generated 3 exercises using GigaChat LLM
✅ Translation evaluated using GigaChat LLM
```

### При ошибке LLM:
```
LLM generation failed: Client error '400 Bad Request' for url 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
📤 POST /lesson/start → 503

LLM evaluation failed: Connection timeout
📤 POST /lesson/evaluate → 503
```

## 🚀 Что делать пользователю

Если пользователь видит сообщение "Сервис временно недоступен":

1. **Подождите и попробуйте позже** - возможно GigaChat API временно недоступен
2. **Проверьте интернет-соединение** - убедитесь что есть доступ к интернету
3. **Обратитесь к администратору** - если проблема сохраняется, возможно не настроены credentials

## 🔧 Что делать администратору

Если пользователи жалуются на недоступность сервиса:

1. **Проверьте credentials в `.env`:**
   ```env
   GIGACHAT_CLIENT_ID=your-client-id
   GIGACHAT_CLIENT_SECRET=your-client-secret
   ```

2. **Проверьте логи backend:**
   ```bash
   # Ищите ошибки LLM
   grep "LLM.*failed" backend.log
   ```

3. **Проверьте доступность GigaChat API:**
   ```bash
   curl -I https://gigachat.devices.sberbank.ru
   ```

4. **Проверьте лимиты:**
   - Для физических лиц есть бесплатный лимит
   - Для ИП/ЮЛ нужно покупать токены

5. **Перезапустите backend:**
   ```bash
   uvicorn main:app --reload
   ```

## 📚 Связанные документы

- [Настройка GigaChat API](./GIGACHAT_SETUP.md) - как получить credentials
- [Полный запуск](./FULL_STACK_LAUNCH.md) - запуск всего стека

## 🎯 Итог

✅ Backend возвращает ошибку 503 при недоступности LLM  
✅ Frontend показывает понятное сообщение пользователю  
✅ Логи показывают причину ошибки  
✅ Нет fallback механизма - если LLM недоступен, урок не может быть начат  

**Рекомендация:** Для production обязательно настройте GigaChat API credentials. Без LLM приложение не может генерировать упражнения и оценивать переводы.
