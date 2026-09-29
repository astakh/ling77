"""
Тестовый скрипт для проверки подключения к GigaChat API.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings

print("=" * 60)
print("🔍 Проверка подключения к GigaChat API")
print("=" * 60)

# Проверка 1: SDK установлен
print("\n1️⃣  Проверка установки SDK...")
try:
    from gigachat import GigaChat
    print("   ✅ GigaChat SDK установлен")
except ImportError:
    print("   ❌ GigaChat SDK не установлен!")
    print("   Выполните: pip install gigachat")
    sys.exit(1)

# Проверка 2: Authorization Key настроен
print("\n2️⃣  Проверка Authorization Key...")
if not settings.GIGACHAT_AUTH_KEY:
    print("   ❌ GIGACHAT_AUTH_KEY не настроен!")
    print("   Откройте backend/.env и добавьте:")
    print("   GIGACHAT_AUTH_KEY=ваш-ключ-из-studio")
    sys.exit(1)

print(f"   ✅ Authorization Key настроен")
print(f"   Preview: {settings.GIGACHAT_AUTH_KEY[:30]}...")
print(f"   Length: {len(settings.GIGACHAT_AUTH_KEY)} chars")

# Проверка 3: Формат ключа
print("\n3️⃣  Проверка формата ключа...")
if ":" not in settings.GIGACHAT_AUTH_KEY:
    print("   ⚠️  Authorization Key не содержит ':'")
    print("   Ожидаемый формат: UUID:base64string")
    print("   Возможно это неправильный ключ")
else:
    parts = settings.GIGACHAT_AUTH_KEY.split(":", 1)
    print(f"   ✅ Формат правильный")
    print(f"   UUID: {parts[0][:8]}...")
    print(f"   Base64 part length: {len(parts[1])} chars")

# Проверка 4: Инициализация клиента
print("\n4️⃣  Инициализация GigaChat клиента...")
try:
    giga = GigaChat(
        credentials=settings.GIGACHAT_AUTH_KEY,
        scope="GIGACHAT_API_PERS",
        verify_certs=False,
    )
    print("   ✅ Клиент инициализирован")
except Exception as e:
    print(f"   ❌ Ошибка инициализации: {e}")
    sys.exit(1)

# Проверка 5: Тестовый запрос
print("\n5️⃣  Тестовый запрос к API...")
try:
    from gigachat.models import Chat, Messages
    
    response = giga.chat(
        Chat(
            model="GigaChat-3-Ultra",  # Явно указываем модель
            messages=[
                Messages(role="user", content="Скажи 'Привет' одним словом")
            ],
            temperature=0.1,
            max_tokens=10,
        )
    )
    
    content = response.choices[0].message.content
    print(f"   ✅ Ответ получен: {content}")
    
    if hasattr(response, 'usage') and response.usage:
        print(f"   Tokens used: {response.usage.total_tokens}")
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("=" * 60)
    print("\n🎉 GigaChat API готов к использованию!")
    print("\nСледующие шаги:")
    print("1. Перезапустите backend: uvicorn main:app --reload")
    print("2. Откройте http://localhost:3000")
    print("3. Начните урок")
    
except Exception as e:
    print(f"   ❌ Ошибка запроса: {e}")
    print("\n" + "=" * 60)
    print("❌ ТЕСТ НЕ ПРОЙДЕН")
    print("=" * 60)
    print("\nВозможные причины:")
    print("1. Неправильный Authorization Key")
    print("2. Нет доступа к GigaChat API")
    print("3. Проблемы с сетью")
    print("4. SSL сертификат не установлен")
    print("\nРешение:")
    print("- Проверьте Authorization Key в личном кабинете")
    print("- Убедитесь что проект активен")
    print("- Проверьте интернет-соединение")
    sys.exit(1)
