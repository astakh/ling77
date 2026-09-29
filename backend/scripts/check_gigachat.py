"""
Проверка конфигурации GigaChat
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings

print("=" * 60)
print("🔍 Проверка конфигурации GigaChat")
print("=" * 60)

print("\n📋 Настройки из .env:")
print(f"   GIGACHAT_CLIENT_ID: {settings.GIGACHAT_CLIENT_ID or '❌ NOT SET'}")
print(f"   GIGACHAT_CLIENT_SECRET: {'✅ SET' if settings.GIGACHAT_CLIENT_SECRET else '❌ NOT SET'}")
print(f"   GIGACHAT_AUTH_URL: {settings.GIGACHAT_AUTH_URL}")
print(f"   GIGACHAT_API_URL: {settings.GIGACHAT_API_URL}")

if not settings.GIGACHAT_CLIENT_ID or not settings.GIGACHAT_CLIENT_SECRET:
    print("\n❌ ОШИБКА: GigaChat credentials не настроены!")
    print("\n📝 Что нужно сделать:")
    print("   1. Откройте backend/.env")
    print("   2. Добавьте:")
    print("      GIGACHAT_CLIENT_ID=your-client-id")
    print("      GIGACHAT_CLIENT_SECRET=your-client-secret")
    print("   3. Перезапустите backend: uvicorn main:app --reload")
    print("\n📚 Как получить credentials:")
    print("   https://developers.sber.ru/studio")
    sys.exit(1)

print("\n✅ Credentials настроены")

# Проверяем формат
import base64
credentials = f"{settings.GIGACHAT_CLIENT_ID}:{settings.GIGACHAT_CLIENT_SECRET}"
auth_key = base64.b64encode(credentials.encode()).decode()

print(f"\n🔐 Authorization Key:")
print(f"   Client ID (первые 8 символов): {settings.GIGACHAT_CLIENT_ID[:8]}...")
print(f"   Client Secret: {'✅ SET' if settings.GIGACHAT_CLIENT_SECRET else '❌ NOT SET'}")
print(f"   Auth Key (первые 20 символов): {auth_key[:20]}...")
print(f"   Auth Key длина: {len(auth_key)} символов")

print("\n" + "=" * 60)
print("✅ Конфигурация выглядит правильно!")
print("=" * 60)
print("\n💡 Если всё равно получаете ошибку 400:")
print("   1. Проверьте что Client ID и Client Secret правильные")
print("   2. Убедитесь что нет лишних пробелов в .env")
print("   3. Перезапустите backend")
print("   4. Проверьте логи backend для деталей")
