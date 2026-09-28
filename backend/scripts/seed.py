"""
Seed script — populates the database with default dictionaries and words.
Run after migrations: python scripts/seed.py
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


# Initial dictionaries with categories
DICTIONARIES = [
    # General dictionaries by level
    {
        "name": "Базовый словарь A1",
        "description": "Самые частотные слова для начинающих",
        "category": "general",
    },
    {
        "name": "Элементарный словарь A2",
        "description": "Слова для повседневного общения",
        "category": "general",
    },
    {
        "name": "Средний словарь B1",
        "description": "Слова для свободного общения на знакомые темы",
        "category": "general",
    },
    {
        "name": "Продвинутый словарь B2",
        "description": "Сложные слова для абстрактных тем",
        "category": "general",
    },
    {
        "name": "Общий словарь (A1-B2)",
        "description": "Объединённый словарь со словами всех уровней",
        "category": "general",
    },
    # Thematic dictionaries
    {
        "name": "IT и технологии",
        "description": "Словарь для IT-специалистов: программирование, сети, железо",
        "category": "it",
    },
    {
        "name": "Путешествия",
        "description": "Слова для путешественников: транспорт, отели, достопримечательности",
        "category": "travel",
    },
    {
        "name": "Бизнес и работа",
        "description": "Деловая лексика: переговоры, финансы, управление",
        "category": "business",
    },
    {
        "name": "Еда и рестораны",
        "description": "Кулинарная лексика: продукты, блюда, заказ в ресторане",
        "category": "food",
    },
    {
        "name": "Медицина и здоровье",
        "description": "Медицинские термины и слова о здоровье",
        "category": "medical",
    },
]


# Words data (from frontend/src/data/words.ts)
WORDS = [
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

# Thematic words for specific dictionaries
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
        {"lemma": "itinerary", "pos": "noun", "level": "B1", "translations": ["маршрут", "итinerary"]},
        {"lemma": "souvenir", "pos": "noun", "level": "A2", "translations": ["сувенир"]},
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
    ],
    "food": [
        {"lemma": "recipe", "pos": "noun", "level": "A2", "translations": ["рецепт"]},
        {"lemma": "ingredient", "pos": "noun", "level": "B1", "translations": ["ингредиент"]},
        {"lemma": "appetizer", "pos": "noun", "level": "B1", "translations": ["закуска"]},
        {"lemma": "dessert", "pos": "noun", "level": "A2", "translations": ["десерт"]},
        {"lemma": "beverage", "pos": "noun", "level": "B1", "translations": ["напиток"]},
        {"lemma": "menu", "pos": "noun", "level": "A1", "translations": ["меню"]},
        {"lemma": "reservation", "pos": "noun", "level": "B1", "translations": ["бронь", "резерв"]},
        {"lemma": "waiter", "pos": "noun", "level": "A2", "translations": ["официант"]},
        {"lemma": "bill", "pos": "noun", "level": "A2", "translations": ["счёт"]},
        {"lemma": "tip", "pos": "noun", "level": "A2", "translations": ["чаевые"]},
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
    ],
}


def make_lemma_key(lemma: str) -> str:
    return unicodedata.normalize("NFC", lemma).casefold().strip()


async def seed():
    async with async_session_factory() as session:
        # 1. Create dictionaries
        print("Creating dictionaries...")
        dict_map = {}  # name -> Dictionary
        for d_data in DICTIONARIES:
            result = await session.execute(
                select(Dictionary).where(Dictionary.name == d_data["name"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                dict_map[d_data["name"]] = existing
                print(f"  ✓ Dictionary '{d_data['name']}' already exists (id={existing.id})")
            else:
                d = Dictionary(
                    name=d_data["name"],
                    description=d_data["description"],
                    category=d_data["category"],
                )
                session.add(d)
                await session.flush()
                dict_map[d_data["name"]] = d
                print(f"  + Created dictionary '{d.name}' (id={d.id}, category={d.category})")

        # 2. Add words to level-specific dictionaries
        print("\nAdding words to dictionaries...")
        level_to_dict = {
            "A1": dict_map["Базовый словарь A1"],
            "A2": dict_map["Элементарный словарь A2"],
            "B1": dict_map["Средний словарь B1"],
            "B2": dict_map["Продвинутый словарь B2"],
        }
        combined_dict = dict_map["Общий словарь (A1-B2)"]

        created_count = 0
        skipped_count = 0

        for word_data in WORDS:
            lemma_key = make_lemma_key(word_data["lemma"])
            level = word_data["level"]

            # Check if word exists globally
            result = await session.execute(
                select(Word).where(
                    Word.lemma_key == lemma_key,
                    Word.pos == word_data["pos"],
                )
            )
            word = result.scalar_one_or_none()
            
            # Create word if it doesn't exist
            if not word:
                word = Word(
                    lemma=word_data["lemma"],
                    lemma_key=lemma_key,
                    pos=word_data["pos"],
                    level=level,
                    translations=word_data["translations"],
                )
                session.add(word)
                await session.flush()
                created_count += 1

            # Add to level-specific dictionary
            target_dict = level_to_dict[level]
            result = await session.execute(
                select(DictionaryWord).where(
                    DictionaryWord.dictionary_id == target_dict.id,
                    DictionaryWord.word_id == word.id,
                )
            )
            if not result.scalar_one_or_none():
                link = DictionaryWord(
                    dictionary_id=target_dict.id,
                    word_id=word.id,
                )
                session.add(link)
                created_count += 1

            # Add to combined dictionary
            result = await session.execute(
                select(DictionaryWord).where(
                    DictionaryWord.dictionary_id == combined_dict.id,
                    DictionaryWord.word_id == word.id,
                )
            )
            if not result.scalar_one_or_none():
                link = DictionaryWord(
                    dictionary_id=combined_dict.id,
                    word_id=word.id,
                )
                session.add(link)
                created_count += 1
            else:
                skipped_count += 1

        # 4. Add thematic words to thematic dictionaries
        print("\nAdding thematic words...")
        thematic_dict_map = {
            "it": dict_map.get("IT и технологии"),
            "travel": dict_map.get("Путешествия"),
            "business": dict_map.get("Бизнес и работа"),
            "food": dict_map.get("Еда и рестораны"),
            "medical": dict_map.get("Медицина и здоровье"),
        }
        
        for category, words_list in THEMATIC_WORDS.items():
            target_dict = thematic_dict_map.get(category)
            if not target_dict:
                print(f"  ⚠️  Skipping {category} - dictionary not found")
                continue
            
            for word_data in words_list:
                lemma_key = make_lemma_key(word_data["lemma"])
                
                # Check if word exists
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
                    created_count += 1
                
                # Link to thematic dictionary
                result = await session.execute(
                    select(DictionaryWord).where(
                        DictionaryWord.dictionary_id == target_dict.id,
                        DictionaryWord.word_id == word.id,
                    )
                )
                if not result.scalar_one_or_none():
                    link = DictionaryWord(
                        dictionary_id=target_dict.id,
                        word_id=word.id,
                    )
                    session.add(link)
                    created_count += 1
                
                # Also link to combined dictionary
                result = await session.execute(
                    select(DictionaryWord).where(
                        DictionaryWord.dictionary_id == combined_dict.id,
                        DictionaryWord.word_id == word.id,
                    )
                )
                if not result.scalar_one_or_none():
                    link = DictionaryWord(
                        dictionary_id=combined_dict.id,
                        word_id=word.id,
                    )
                    session.add(link)
        
        await session.commit()
        print(f"\n✓ Done! Created {created_count} word entries, skipped {skipped_count}")

        # 5. Print summary
        print("\n=== Summary ===")
        for name, d in dict_map.items():
            result = await session.execute(
                select(DictionaryWord).where(DictionaryWord.dictionary_id == d.id)
            )
            count = len(result.scalars().all())
            print(f"  {name} [{d.category}]: {count} words")


if __name__ == "__main__":
    asyncio.run(seed())
