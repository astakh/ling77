"""
Seed script — populates the database with dictionaries and words.

Architecture:
- `dictionaries` — thematic dictionaries (general, it, travel, business, etc.)
- `words` — unique words with their own level (A1-B2)
- `dictionary_words` — M:N link (one word can be in multiple dictionaries)
- `learning_profiles.level` — user's level (filters which words are shown)

A word's level is independent of the dictionary it belongs to.
"""

import asyncio
import unicodedata
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from database import async_session_factory
from models import Dictionary, Word, DictionaryWord


# Thematic dictionaries (NO level-based dictionaries!)
DICTIONARIES = [
    {
        "name": "Общий словарь",
        "description": "Все слова приложения. Включает слова из всех тематических словарей. (Скрыт от пользователей)",
        "category": "general",
        "is_public": False,  # Скрываем от пользователей
    },
    {
        "name": "IT и технологии",
        "description": "Программирование, сети, железо, разработка",
        "category": "it",
    },
    {
        "name": "Путешествия",
        "description": "Транспорт, отели, достопримечательности, аэропорты",
        "category": "travel",
    },
    {
        "name": "Бизнес и работа",
        "description": "Переговоры, финансы, управление, офис",
        "category": "business",
    },
    {
        "name": "Еда и рестораны",
        "description": "Продукты, блюда, заказ в ресторане, кулинария",
        "category": "food",
    },
    {
        "name": "Медицина и здоровье",
        "description": "Медицинские термины, здоровье, аптека",
        "category": "medical",
    },
    {
        "name": "Повседневное общение",
        "description": "Базовые слова для ежедневного общения",
        "category": "daily",
    },
]


# General everyday words (go to "Общий словарь" + "Повседневное общение")
GENERAL_WORDS = [
    # A1
    {"lemma": "house", "pos": "noun", "level": "A1", "translations": ["дом", "жилище"]},
    {"lemma": "water", "pos": "noun", "level": "A1", "translations": ["вода"]},
    {"lemma": "food", "pos": "noun", "level": "A1", "translations": ["еда", "пища"]},
    {"lemma": "book", "pos": "noun", "level": "A1", "translations": ["книга"]},
    {"lemma": "friend", "pos": "noun", "level": "A1", "translations": ["друг", "подруга"]},
    {"lemma": "school", "pos": "noun", "level": "A1", "translations": ["школа"]},
    {"lemma": "work", "pos": "noun", "level": "A1", "translations": ["работа", "труд"]},
    {"lemma": "time", "pos": "noun", "level": "A1", "translations": ["время"]},
    {"lemma": "day", "pos": "noun", "level": "A1", "translations": ["день"]},
    {"lemma": "night", "pos": "noun", "level": "A1", "translations": ["ночь"]},
    {"lemma": "big", "pos": "adjective", "level": "A1", "translations": ["большой", "крупный"]},
    {"lemma": "small", "pos": "adjective", "level": "A1", "translations": ["маленький", "небольшой"]},
    {"lemma": "good", "pos": "adjective", "level": "A1", "translations": ["хороший", "добрый"]},
    {"lemma": "bad", "pos": "adjective", "level": "A1", "translations": ["плохой"]},
    {"lemma": "run", "pos": "verb", "level": "A1", "translations": ["бежать", "бегать"]},
    {"lemma": "eat", "pos": "verb", "level": "A1", "translations": ["есть", "кушать"]},
    {"lemma": "sleep", "pos": "verb", "level": "A1", "translations": ["спать"]},
    {"lemma": "read", "pos": "verb", "level": "A1", "translations": ["читать"]},
    {"lemma": "write", "pos": "verb", "level": "A1", "translations": ["писать"]},
    {"lemma": "go", "pos": "verb", "level": "A1", "translations": ["идти", "ехать"]},

    # A2
    {"lemma": "journey", "pos": "noun", "level": "A2", "translations": ["путешествие", "поездка"]},
    {"lemma": "weather", "pos": "noun", "level": "A2", "translations": ["погода"]},
    {"lemma": "kitchen", "pos": "noun", "level": "A2", "translations": ["кухня"]},
    {"lemma": "garden", "pos": "noun", "level": "A2", "translations": ["сад"]},
    {"lemma": "bridge", "pos": "noun", "level": "A2", "translations": ["мост"]},
    {"lemma": "quiet", "pos": "adjective", "level": "A2", "translations": ["тихий", "спокойный"]},
    {"lemma": "bright", "pos": "adjective", "level": "A2", "translations": ["яркий", "светлый"]},
    {"lemma": "narrow", "pos": "adjective", "level": "A2", "translations": ["узкий"]},
    {"lemma": "arrive", "pos": "verb", "level": "A2", "translations": ["прибывать", "приезжать"]},
    {"lemma": "discover", "pos": "verb", "level": "A2", "translations": ["открывать", "обнаруживать"]},
    {"lemma": "remember", "pos": "verb", "level": "A2", "translations": ["помнить", "вспоминать"]},
    {"lemma": "promise", "pos": "verb", "level": "A2", "translations": ["обещать"]},
    {"lemma": "borrow", "pos": "verb", "level": "A2", "translations": ["одалживать", "занимать"]},
    {"lemma": "suggest", "pos": "verb", "level": "A2", "translations": ["предлагать"]},
    {"lemma": "comfortable", "pos": "adjective", "level": "A2", "translations": ["удобный", "комфортный"]},
    {"lemma": "dangerous", "pos": "adjective", "level": "A2", "translations": ["опасный"]},
    {"lemma": "ancient", "pos": "adjective", "level": "A2", "translations": ["древний", "старинный"]},
    {"lemma": "village", "pos": "noun", "level": "A2", "translations": ["деревня", "село"]},
    {"lemma": "market", "pos": "noun", "level": "A2", "translations": ["рынок", "маркет"]},
    {"lemma": "forest", "pos": "noun", "level": "A2", "translations": ["лес"]},

    # B1
    {"lemma": "achievement", "pos": "noun", "level": "B1", "translations": ["достижение"]},
    {"lemma": "opportunity", "pos": "noun", "level": "B1", "translations": ["возможность"]},
    {"lemma": "environment", "pos": "noun", "level": "B1", "translations": ["окружение", "среда"]},
    {"lemma": "responsibility", "pos": "noun", "level": "B1", "translations": ["ответственность"]},
    {"lemma": "influence", "pos": "noun", "level": "B1", "translations": ["влияние"]},
    {"lemma": "negotiate", "pos": "verb", "level": "B1", "translations": ["вести переговоры"]},
    {"lemma": "persuade", "pos": "verb", "level": "B1", "translations": ["убеждать"]},
    {"lemma": "investigate", "pos": "verb", "level": "B1", "translations": ["расследовать", "исследовать"]},
    {"lemma": "consider", "pos": "verb", "level": "B1", "translations": ["рассматривать", "обдумывать"]},
    {"lemma": "remarkable", "pos": "adjective", "level": "B1", "translations": ["замечательный", "необычный"]},
    {"lemma": "significant", "pos": "adjective", "level": "B1", "translations": ["значительный", "важный"]},
    {"lemma": "temporary", "pos": "adjective", "level": "B1", "translations": ["временный"]},
    {"lemma": "consequence", "pos": "noun", "level": "B1", "translations": ["последствие", "результат"]},
    {"lemma": "approach", "pos": "noun", "level": "B1", "translations": ["подход", "приближение"]},
    {"lemma": "evidence", "pos": "noun", "level": "B1", "translations": ["доказательство", "свидетельство"]},

    # B2
    {"lemma": "sophisticated", "pos": "adjective", "level": "B2", "translations": ["утончённый", "сложный"]},
    {"lemma": "controversial", "pos": "adjective", "level": "B2", "translations": ["спорный", "противоречивый"]},
    {"lemma": "comprehensive", "pos": "adjective", "level": "B2", "translations": ["всеобъемлющий", "комплексный"]},
    {"lemma": "inevitable", "pos": "adjective", "level": "B2", "translations": ["неизбежный"]},
    {"lemma": "implement", "pos": "verb", "level": "B2", "translations": ["внедрять", "осуществлять"]},
    {"lemma": "acknowledge", "pos": "verb", "level": "B2", "translations": ["признавать"]},
    {"lemma": "deteriorate", "pos": "verb", "level": "B2", "translations": ["ухудшаться"]},
    {"lemma": "phenomenon", "pos": "noun", "level": "B2", "translations": ["явление", "феномен"]},
    {"lemma": "dilemma", "pos": "noun", "level": "B2", "translations": ["дилемма"]},
    {"lemma": "breakthrough", "pos": "noun", "level": "B2", "translations": ["прорыв"]},
]


# Thematic words (go to thematic dictionary + "Общий словарь")
THEMATIC_WORDS = {
    "it": [
        {"lemma": "algorithm", "pos": "noun", "level": "B1", "translations": ["алгоритм"]},
        {"lemma": "database", "pos": "noun", "level": "B1", "translations": ["база данных"]},
        {"lemma": "server", "pos": "noun", "level": "A2", "translations": ["сервер"]},
        {"lemma": "deploy", "pos": "verb", "level": "B1", "translations": ["разворачивать", "деплоить"]},
        {"lemma": "debug", "pos": "verb", "level": "B1", "translations": ["отлаживать"]},
        {"lemma": "compile", "pos": "verb", "level": "B1", "translations": ["компилировать"]},
        {"lemma": "repository", "pos": "noun", "level": "B1", "translations": ["репозиторий"]},
        {"lemma": "framework", "pos": "noun", "level": "B1", "translations": ["фреймворк"]},
        {"lemma": "interface", "pos": "noun", "level": "B1", "translations": ["интерфейс"]},
        {"lemma": "variable", "pos": "noun", "level": "A2", "translations": ["переменная"]},
        {"lemma": "function", "pos": "noun", "level": "B1", "translations": ["функция"]},
        {"lemma": "code", "pos": "noun", "level": "A2", "translations": ["код"]},
        {"lemma": "bug", "pos": "noun", "level": "A2", "translations": ["ошибка", "баг"]},
        {"lemma": "feature", "pos": "noun", "level": "B1", "translations": ["функция", "возможность"]},
        {"lemma": "release", "pos": "noun", "level": "B1", "translations": ["релиз", "выпуск"]},
    ],
    "travel": [
        {"lemma": "airport", "pos": "noun", "level": "A1", "translations": ["аэропорт"]},
        {"lemma": "ticket", "pos": "noun", "level": "A1", "translations": ["билет"]},
        {"lemma": "hotel", "pos": "noun", "level": "A1", "translations": ["отель", "гостиница"]},
        {"lemma": "luggage", "pos": "noun", "level": "A2", "translations": ["багаж"]},
        {"lemma": "departure", "pos": "noun", "level": "A2", "translations": ["отправление"]},
        {"lemma": "arrival", "pos": "noun", "level": "A2", "translations": ["прибытие"]},
        {"lemma": "boarding pass", "pos": "noun", "level": "A2", "translations": ["посадочный талон"]},
        {"lemma": "customs", "pos": "noun", "level": "B1", "translations": ["таможня"]},
        {"lemma": "itinerary", "pos": "noun", "level": "B1", "translations": ["маршрут"]},
        {"lemma": "souvenir", "pos": "noun", "level": "A2", "translations": ["сувенир"]},
        {"lemma": "flight", "pos": "noun", "level": "A2", "translations": ["рейс", "полёт"]},
        {"lemma": "passport", "pos": "noun", "level": "A1", "translations": ["паспорт"]},
        {"lemma": "reservation", "pos": "noun", "level": "B1", "translations": ["бронирование"]},
        {"lemma": "destination", "pos": "noun", "level": "B1", "translations": ["назначение", "место назначения"]},
        {"lemma": "boarding", "pos": "noun", "level": "B1", "translations": ["посадка"]},
    ],
    "business": [
        {"lemma": "deadline", "pos": "noun", "level": "B1", "translations": ["дедлайн", "срок"]},
        {"lemma": "negotiation", "pos": "noun", "level": "B1", "translations": ["переговоры"]},
        {"lemma": "profit", "pos": "noun", "level": "B1", "translations": ["прибыль"]},
        {"lemma": "revenue", "pos": "noun", "level": "B1", "translations": ["выручка", "доход"]},
        {"lemma": "stakeholder", "pos": "noun", "level": "B2", "translations": ["стейкхолдер", "заинтересованная сторона"]},
        {"lemma": "budget", "pos": "noun", "level": "A2", "translations": ["бюджет"]},
        {"lemma": "invoice", "pos": "noun", "level": "B1", "translations": ["счёт", "инвойс"]},
        {"lemma": "contract", "pos": "noun", "level": "B1", "translations": ["контракт", "договор"]},
        {"lemma": "proposal", "pos": "noun", "level": "B1", "translations": ["предложение", "пропозиция"]},
        {"lemma": "meeting", "pos": "noun", "level": "A2", "translations": ["встреча", "совещание"]},
        {"lemma": "client", "pos": "noun", "level": "A2", "translations": ["клиент"]},
        {"lemma": "manager", "pos": "noun", "level": "A2", "translations": ["менеджер", "управляющий"]},
        {"lemma": "salary", "pos": "noun", "level": "A2", "translations": ["зарплата"]},
        {"lemma": "interview", "pos": "noun", "level": "B1", "translations": ["интервью", "собеседование"]},
        {"lemma": "promotion", "pos": "noun", "level": "B1", "translations": ["повышение", "продвижение"]},
    ],
    "food": [
        {"lemma": "recipe", "pos": "noun", "level": "A2", "translations": ["рецепт"]},
        {"lemma": "ingredient", "pos": "noun", "level": "B1", "translations": ["ингредиент"]},
        {"lemma": "appetizer", "pos": "noun", "level": "B1", "translations": ["закуска"]},
        {"lemma": "dessert", "pos": "noun", "level": "A2", "translations": ["десерт"]},
        {"lemma": "beverage", "pos": "noun", "level": "B1", "translations": ["напиток"]},
        {"lemma": "menu", "pos": "noun", "level": "A1", "translations": ["меню"]},
        {"lemma": "waiter", "pos": "noun", "level": "A2", "translations": ["официант"]},
        {"lemma": "bill", "pos": "noun", "level": "A2", "translations": ["счёт"]},
        {"lemma": "tip", "pos": "noun", "level": "A2", "translations": ["чаевые"]},
        {"lemma": "spicy", "pos": "adjective", "level": "A2", "translations": ["острый", "пряный"]},
        {"lemma": "delicious", "pos": "adjective", "level": "A2", "translations": ["вкусный"]},
        {"lemma": "bake", "pos": "verb", "level": "A2", "translations": ["печь", "запекать"]},
        {"lemma": "boil", "pos": "verb", "level": "A2", "translations": ["кипятить", "варить"]},
        {"lemma": "fry", "pos": "verb", "level": "A2", "translations": ["жарить"]},
        {"lemma": "slice", "pos": "verb", "level": "A2", "translations": ["нарезать"]},
    ],
    "medical": [
        {"lemma": "symptom", "pos": "noun", "level": "B1", "translations": ["симптом"]},
        {"lemma": "diagnosis", "pos": "noun", "level": "B1", "translations": ["диагноз"]},
        {"lemma": "treatment", "pos": "noun", "level": "B1", "translations": ["лечение"]},
        {"lemma": "prescription", "pos": "noun", "level": "B1", "translations": ["рецепт", "назначение"]},
        {"lemma": "pharmacy", "pos": "noun", "level": "A2", "translations": ["аптека"]},
        {"lemma": "surgeon", "pos": "noun", "level": "B1", "translations": ["хирург"]},
        {"lemma": "therapy", "pos": "noun", "level": "B1", "translations": ["терапия"]},
        {"lemma": "vaccine", "pos": "noun", "level": "B1", "translations": ["вакцина"]},
        {"lemma": "allergy", "pos": "noun", "level": "B1", "translations": ["аллергия"]},
        {"lemma": "appointment", "pos": "noun", "level": "A2", "translations": ["приём", "запись"]},
        {"lemma": "headache", "pos": "noun", "level": "A2", "translations": ["головная боль"]},
        {"lemma": "fever", "pos": "noun", "level": "A2", "translations": ["температура", "жар"]},
        {"lemma": "recover", "pos": "verb", "level": "B1", "translations": ["выздоравливать"]},
        {"lemma": "examine", "pos": "verb", "level": "B1", "translations": ["осматривать"]},
        {"lemma": "prescribe", "pos": "verb", "level": "B1", "translations": ["прописывать", "назначать"]},
    ],
}


def make_lemma_key(lemma: str) -> str:
    return unicodedata.normalize("NFC", lemma).casefold().strip()


async def get_or_create_word(session, word_data: dict) -> Word:
    """Get existing word or create a new one. Returns the Word instance."""
    lemma_key = make_lemma_key(word_data["lemma"])
    
    result = await session.execute(
        select(Word).where(
            Word.lemma_key == lemma_key,
            Word.pos == word_data["pos"],
        )
    )
    word = result.scalar_one_or_none()
    
    if not word:
        word = Word(
            lemma=word_data["lemma"],
            lemma_key=lemma_key,
            pos=word_data["pos"],
            level=word_data["level"],
            translations=word_data["translations"],
        )
        session.add(word)
        await session.flush()
        return word, True  # created
    
    return word, False  # existing


async def link_word_to_dictionary(session, dictionary_id: int, word_id: int) -> bool:
    """Link word to dictionary. Returns True if link was created, False if already exists."""
    result = await session.execute(
        select(DictionaryWord).where(
            DictionaryWord.dictionary_id == dictionary_id,
            DictionaryWord.word_id == word_id,
        )
    )
    if result.scalar_one_or_none():
        return False
    
    link = DictionaryWord(dictionary_id=dictionary_id, word_id=word_id)
    session.add(link)
    return True


async def seed():
    async with async_session_factory() as session:
        # 1. Create dictionaries
        print("=" * 60)
        print("📚 Creating dictionaries...")
        print("=" * 60)
        
        dict_map = {}  # name -> Dictionary
        for d_data in DICTIONARIES:
            result = await session.execute(
                select(Dictionary).where(Dictionary.name == d_data["name"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                dict_map[d_data["name"]] = existing
                print(f"  ✓ '{d_data['name']}' already exists (id={existing.id}, category={existing.category})")
            else:
                d = Dictionary(
                    name=d_data["name"],
                    description=d_data["description"],
                    category=d_data["category"],
                    is_public=d_data.get("is_public", True),  # По умолчанию True
                )
                session.add(d)
                await session.flush()
                dict_map[d_data["name"]] = d
                print(f"  + Created '{d.name}' (id={d.id}, category={d.category})")
        
        general_dict = dict_map["Общий словарь"]
        daily_dict = dict_map["Повседневное общение"]
        
        # 2. Add general words to "Общий словарь" + "Повседневное общение"
        print("\n" + "=" * 60)
        print("📝 Adding general words...")
        print("=" * 60)
        
        created_words = 0
        created_links = 0
        skipped_links = 0
        
        for word_data in GENERAL_WORDS:
            word, was_created = await get_or_create_word(session, word_data)
            if was_created:
                created_words += 1
            
            # Link to general dictionary
            if await link_word_to_dictionary(session, general_dict.id, word.id):
                created_links += 1
            else:
                skipped_links += 1
            
            # Link to daily dictionary
            if await link_word_to_dictionary(session, daily_dict.id, word.id):
                created_links += 1
            else:
                skipped_links += 1
        
        print(f"  ✅ Words created: {created_words}")
        print(f"  🔗 Links created: {created_links}")
        print(f"  ⏭️  Links skipped (already exist): {skipped_links}")
        
        # 3. Add thematic words to their dictionaries + general
        print("\n" + "=" * 60)
        print("🎯 Adding thematic words...")
        print("=" * 60)
        
        thematic_dict_map = {
            "it": dict_map["IT и технологии"],
            "travel": dict_map["Путешествия"],
            "business": dict_map["Бизнес и работа"],
            "food": dict_map["Еда и рестораны"],
            "medical": dict_map["Медицина и здоровье"],
        }
        
        for category, words_list in THEMATIC_WORDS.items():
            target_dict = thematic_dict_map[category]
            cat_created = 0
            cat_links = 0
            
            for word_data in words_list:
                word, was_created = await get_or_create_word(session, word_data)
                if was_created:
                    created_words += 1
                    cat_created += 1
                
                # Link to thematic dictionary
                if await link_word_to_dictionary(session, target_dict.id, word.id):
                    created_links += 1
                    cat_links += 1
                
                # Also link to general dictionary (all words are in general)
                if await link_word_to_dictionary(session, general_dict.id, word.id):
                    created_links += 1
            
            print(f"  📁 {target_dict.name}: {cat_created} new words, {cat_links} new links")
        
        await session.commit()
        
        # 4. Print summary
        print("\n" + "=" * 60)
        print("📊 Summary")
        print("=" * 60)
        print(f"  Total unique words created: {created_words}")
        print(f"  Total dictionary-word links: {created_links}")
        print()
        
        for name, d in dict_map.items():
            result = await session.execute(
                select(DictionaryWord).where(DictionaryWord.dictionary_id == d.id)
            )
            count = len(result.scalars().all())
            print(f"  📚 {name} [{d.category}]: {count} words")
        
        print("\n" + "=" * 60)
        print("✅ Done!")
        print("=" * 60)
        print("\n💡 Note: Word level (A1-B2) is a property of the WORD, not the dictionary.")
        print("   User's level (in learning_profiles) filters which words are shown in lessons.")


if __name__ == "__main__":
    asyncio.run(seed())
