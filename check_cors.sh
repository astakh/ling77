#!/bin/bash

echo "🔧 Проверка CORS конфигурации"
echo "================================"
echo ""

echo "1. Проверка backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend работает на http://localhost:8000"
else
    echo "❌ Backend не отвечает. Запустите: cd backend && uvicorn main:app --reload"
    exit 1
fi

echo ""
echo "2. Проверка CORS заголовков..."
HEADERS=$(curl -I -X OPTIONS http://localhost:8000/auth/register 2>&1 | grep -i "access-control")

if [ -n "$HEADERS" ]; then
    echo "✅ CORS заголовки присутствуют:"
    echo "$HEADERS"
else
    echo "❌ CORS заголовки отсутствуют!"
    echo ""
    echo "Попробуйте:"
    echo "1. Перезапустить backend: cd backend && uvicorn main:app --reload"
    echo "2. Проверить логи backend на наличие ошибок"
fi

echo ""
echo "3. Проверка frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend работает на http://localhost:3000"
else
    echo "❌ Frontend не отвечает. Запустите: npm run dev"
    exit 1
fi

echo ""
echo "================================"
echo "✅ Проверка завершена"
echo ""
echo "Если CORS всё ещё не работает:"
echo "1. Очистите кэш браузера (Ctrl+Shift+R)"
echo "2. Откройте DevTools (F12) → Console"
echo "3. Попробуйте зарегистрироваться"
echo "4. Смотрите логи в консоли браузера и терминале backend"
