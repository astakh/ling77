"""
Скрипт для создания словаря широкой тематики с базовой лексикой.
Этот словарь содержит общие слова повседневного использования без специальной терминологии.

Использование:
    cd backend
    python scripts/create_general_dictionary.py
"""

import asyncio
import sys
import os
import unicodedata

# Добавляем backend в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from database import async_session_factory
from models import Dictionary, Word, DictionaryWord


def make_lemma_key(lemma: str) -> str:
    """Создаем нормализованный ключ леммы"""
    return unicodedata.normalize("NFC", lemma).casefold().strip()


# Базовая лексика широкой тематики (A1-B1)
# Повседневные слова без специальной терминологии
GENERAL_WORDS = [
    # A1 - Базовые слова
    # Существительные
    {"lemma": "time", "pos": "noun", "level": "A1", "translations": ["время"]},
    {"lemma": "year", "pos": "noun", "level": "A1", "translations": ["год"]},
    {"lemma": "people", "pos": "noun", "level": "A1", "translations": ["люди"]},
    {"lemma": "way", "pos": "noun", "level": "A1", "translations": ["путь", "способ"]},
    {"lemma": "day", "pos": "noun", "level": "A1", "translations": ["день"]},
    {"lemma": "man", "pos": "noun", "level": "A1", "translations": ["мужчина"]},
    {"lemma": "woman", "pos": "noun", "level": "A1", "translations": ["женщина"]},
    {"lemma": "child", "pos": "noun", "level": "A1", "translations": ["ребенок"]},
    {"lemma": "world", "pos": "noun", "level": "A1", "translations": ["мир"]},
    {"lemma": "life", "pos": "noun", "level": "A1", "translations": ["жизнь"]},
    {"lemma": "hand", "pos": "noun", "level": "A1", "translations": ["рука"]},
    {"lemma": "part", "pos": "noun", "level": "A1", "translations": ["часть"]},
    {"lemma": "place", "pos": "noun", "level": "A1", "translations": ["место"]},
    {"lemma": "case", "pos": "noun", "level": "A1", "translations": ["случай"]},
    {"lemma": "week", "pos": "noun", "level": "A1", "translations": ["неделя"]},
    {"lemma": "company", "pos": "noun", "level": "A1", "translations": ["компания"]},
    {"lemma": "system", "pos": "noun", "level": "A1", "translations": ["система"]},
    {"lemma": "program", "pos": "noun", "level": "A1", "translations": ["программа"]},
    {"lemma": "question", "pos": "noun", "level": "A1", "translations": ["вопрос"]},
    {"lemma": "work", "pos": "noun", "level": "A1", "translations": ["работа"]},
    {"lemma": "government", "pos": "noun", "level": "A1", "translations": ["правительство"]},
    {"lemma": "number", "pos": "noun", "level": "A1", "translations": ["число"]},
    {"lemma": "night", "pos": "noun", "level": "A1", "translations": ["ночь"]},
    {"lemma": "point", "pos": "noun", "level": "A1", "translations": ["точка"]},
    {"lemma": "home", "pos": "noun", "level": "A1", "translations": ["дом"]},
    {"lemma": "water", "pos": "noun", "level": "A1", "translations": ["вода"]},
    {"lemma": "room", "pos": "noun", "level": "A1", "translations": ["комната"]},
    {"lemma": "mother", "pos": "noun", "level": "A1", "translations": ["мать"]},
    {"lemma": "area", "pos": "noun", "level": "A1", "translations": ["область"]},
    {"lemma": "money", "pos": "noun", "level": "A1", "translations": ["деньги"]},
    {"lemma": "story", "pos": "noun", "level": "A1", "translations": ["история"]},
    {"lemma": "fact", "pos": "noun", "level": "A1", "translations": ["факт"]},
    {"lemma": "month", "pos": "noun", "level": "A1", "translations": ["месяц"]},
    {"lemma": "lot", "pos": "noun", "level": "A1", "translations": ["много"]},
    {"lemma": "right", "pos": "noun", "level": "A1", "translations": ["право"]},
    {"lemma": "study", "pos": "noun", "level": "A1", "translations": ["учеба"]},
    {"lemma": "book", "pos": "noun", "level": "A1", "translations": ["книга"]},
    {"lemma": "eye", "pos": "noun", "level": "A1", "translations": ["глаз"]},
    {"lemma": "job", "pos": "noun", "level": "A1", "translations": ["работа"]},
    {"lemma": "word", "pos": "noun", "level": "A1", "translations": ["слово"]},
    {"lemma": "business", "pos": "noun", "level": "A1", "translations": ["бизнес"]},
    {"lemma": "issue", "pos": "noun", "level": "A1", "translations": ["проблема"]},
    {"lemma": "side", "pos": "noun", "level": "A1", "translations": ["сторона"]},
    {"lemma": "kind", "pos": "noun", "level": "A1", "translations": ["вид"]},
    {"lemma": "head", "pos": "noun", "level": "A1", "translations": ["голова"]},
    {"lemma": "house", "pos": "noun", "level": "A1", "translations": ["дом"]},
    {"lemma": "service", "pos": "noun", "level": "A1", "translations": ["сервис"]},
    {"lemma": "friend", "pos": "noun", "level": "A1", "translations": ["друг"]},
    {"lemma": "father", "pos": "noun", "level": "A1", "translations": ["отец"]},
    {"lemma": "power", "pos": "noun", "level": "A1", "translations": ["сила"]},
    {"lemma": "hour", "pos": "noun", "level": "A1", "translations": ["час"]},
    {"lemma": "game", "pos": "noun", "level": "A1", "translations": ["игра"]},
    {"lemma": "line", "pos": "noun", "level": "A1", "translations": ["линия"]},
    {"lemma": "end", "pos": "noun", "level": "A1", "translations": ["конец"]},
    {"lemma": "member", "pos": "noun", "level": "A1", "translations": ["член"]},
    {"lemma": "law", "pos": "noun", "level": "A1", "translations": ["закон"]},
    {"lemma": "car", "pos": "noun", "level": "A1", "translations": ["машина"]},
    {"lemma": "city", "pos": "noun", "level": "A1", "translations": ["город"]},
    {"lemma": "community", "pos": "noun", "level": "A1", "translations": ["сообщество"]},
    {"lemma": "name", "pos": "noun", "level": "A1", "translations": ["имя"]},
    
    # Глаголы
    {"lemma": "be", "pos": "verb", "level": "A1", "translations": ["быть"]},
    {"lemma": "have", "pos": "verb", "level": "A1", "translations": ["иметь"]},
    {"lemma": "do", "pos": "verb", "level": "A1", "translations": ["делать"]},
    {"lemma": "say", "pos": "verb", "level": "A1", "translations": ["говорить"]},
    {"lemma": "get", "pos": "verb", "level": "A1", "translations": ["получать"]},
    {"lemma": "make", "pos": "verb", "level": "A1", "translations": ["создавать"]},
    {"lemma": "go", "pos": "verb", "level": "A1", "translations": ["идти"]},
    {"lemma": "know", "pos": "verb", "level": "A1", "translations": ["знать"]},
    {"lemma": "take", "pos": "verb", "level": "A1", "translations": ["брать"]},
    {"lemma": "see", "pos": "verb", "level": "A1", "translations": ["видеть"]},
    {"lemma": "come", "pos": "verb", "level": "A1", "translations": ["приходить"]},
    {"lemma": "think", "pos": "verb", "level": "A1", "translations": ["думать"]},
    {"lemma": "look", "pos": "verb", "level": "A1", "translations": ["смотреть"]},
    {"lemma": "want", "pos": "verb", "level": "A1", "translations": ["хотеть"]},
    {"lemma": "give", "pos": "verb", "level": "A1", "translations": ["давать"]},
    {"lemma": "use", "pos": "verb", "level": "A1", "translations": ["использовать"]},
    {"lemma": "find", "pos": "verb", "level": "A1", "translations": ["находить"]},
    {"lemma": "tell", "pos": "verb", "level": "A1", "translations": ["рассказывать"]},
    {"lemma": "ask", "pos": "verb", "level": "A1", "translations": ["спрашивать"]},
    {"lemma": "work", "pos": "verb", "level": "A1", "translations": ["работать"]},
    {"lemma": "seem", "pos": "verb", "level": "A1", "translations": ["казаться"]},
    {"lemma": "feel", "pos": "verb", "level": "A1", "translations": ["чувствовать"]},
    {"lemma": "try", "pos": "verb", "level": "A1", "translations": ["пытаться"]},
    {"lemma": "leave", "pos": "verb", "level": "A1", "translations": ["покидать"]},
    {"lemma": "call", "pos": "verb", "level": "A1", "translations": ["звонить"]},
    
    # Прилагательные
    {"lemma": "good", "pos": "adjective", "level": "A1", "translations": ["хороший"]},
    {"lemma": "new", "pos": "adjective", "level": "A1", "translations": ["новый"]},
    {"lemma": "first", "pos": "adjective", "level": "A1", "translations": ["первый"]},
    {"lemma": "last", "pos": "adjective", "level": "A1", "translations": ["последний"]},
    {"lemma": "long", "pos": "adjective", "level": "A1", "translations": ["длинный"]},
    {"lemma": "great", "pos": "adjective", "level": "A1", "translations": ["великий"]},
    {"lemma": "little", "pos": "adjective", "level": "A1", "translations": ["маленький"]},
    {"lemma": "own", "pos": "adjective", "level": "A1", "translations": ["собственный"]},
    {"lemma": "other", "pos": "adjective", "level": "A1", "translations": ["другой"]},
    {"lemma": "old", "pos": "adjective", "level": "A1", "translations": ["старый"]},
    {"lemma": "right", "pos": "adjective", "level": "A1", "translations": ["правильный"]},
    {"lemma": "big", "pos": "adjective", "level": "A1", "translations": ["большой"]},
    {"lemma": "high", "pos": "adjective", "level": "A1", "translations": ["высокий"]},
    {"lemma": "different", "pos": "adjective", "level": "A1", "translations": ["различный"]},
    {"lemma": "small", "pos": "adjective", "level": "A1", "translations": ["маленький"]},
    {"lemma": "large", "pos": "adjective", "level": "A1", "translations": ["большой"]},
    {"lemma": "next", "pos": "adjective", "level": "A1", "translations": ["следующий"]},
    {"lemma": "early", "pos": "adjective", "level": "A1", "translations": ["ранний"]},
    {"lemma": "young", "pos": "adjective", "level": "A1", "translations": ["молодой"]},
    {"lemma": "important", "pos": "adjective", "level": "A1", "translations": ["важный"]},
    {"lemma": "public", "pos": "adjective", "level": "A1", "translations": ["публичный"]},
    {"lemma": "bad", "pos": "adjective", "level": "A1", "translations": ["плохой"]},
    {"lemma": "same", "pos": "adjective", "level": "A1", "translations": ["одинаковый"]},
    {"lemma": "able", "pos": "adjective", "level": "A1", "translations": ["способный"]},
    
    # A2 - Расширенная базовая лексика
    {"lemma": "family", "pos": "noun", "level": "A2", "translations": ["семья"]},
    {"lemma": "student", "pos": "noun", "level": "A2", "translations": ["студент"]},
    {"lemma": "group", "pos": "noun", "level": "A2", "translations": ["группа"]},
    {"lemma": "country", "pos": "noun", "level": "A2", "translations": ["страна"]},
    {"lemma": "problem", "pos": "noun", "level": "A2", "translations": ["проблема"]},
    {"lemma": "school", "pos": "noun", "level": "A2", "translations": ["школа"]},
    {"lemma": "food", "pos": "noun", "level": "A2", "translations": ["еда"]},
    {"lemma": "family", "pos": "noun", "level": "A2", "translations": ["семья"]},
    {"lemma": "home", "pos": "noun", "level": "A2", "translations": ["дом"]},
    {"lemma": "hand", "pos": "noun", "level": "A2", "translations": ["рука"]},
    {"lemma": "child", "pos": "noun", "level": "A2", "translations": ["ребенок"]},
    {"lemma": "door", "pos": "noun", "level": "A2", "translations": ["дверь"]},
    {"lemma": "health", "pos": "noun", "level": "A2", "translations": ["здоровье"]},
    {"lemma": "person", "pos": "noun", "level": "A2", "translations": ["человек"]},
    {"lemma": "art", "pos": "noun", "level": "A2", "translations": ["искусство"]},
    {"lemma": "war", "pos": "noun", "level": "A2", "translations": ["война"]},
    {"lemma": "history", "pos": "noun", "level": "A2", "translations": ["история"]},
    {"lemma": "party", "pos": "noun", "level": "A2", "translations": ["вечеринка"]},
    {"lemma": "result", "pos": "noun", "level": "A2", "translations": ["результат"]},
    {"lemma": "change", "pos": "noun", "level": "A2", "translations": ["изменение"]},
    {"lemma": "morning", "pos": "noun", "level": "A2", "translations": ["утро"]},
    {"lemma": "reason", "pos": "noun", "level": "A2", "translations": ["причина"]},
    {"lemma": "research", "pos": "noun", "level": "A2", "translations": ["исследование"]},
    {"lemma": "girl", "pos": "noun", "level": "A2", "translations": ["девочка"]},
    {"lemma": "guy", "pos": "noun", "level": "A2", "translations": ["парень"]},
    {"lemma": "moment", "pos": "noun", "level": "A2", "translations": ["момент"]},
    {"lemma": "air", "pos": "noun", "level": "A2", "translations": ["воздух"]},
    {"lemma": "teacher", "pos": "noun", "level": "A2", "translations": ["учитель"]},
    {"lemma": "force", "pos": "noun", "level": "A2", "translations": ["сила"]},
    {"lemma": "education", "pos": "noun", "level": "A2", "translations": ["образование"]},
    
    # Глаголы A2
    {"lemma": "understand", "pos": "verb", "level": "A2", "translations": ["понимать"]},
    {"lemma": "develop", "pos": "verb", "level": "A2", "translations": ["развивать"]},
    {"lemma": "remember", "pos": "verb", "level": "A2", "translations": ["помнить"]},
    {"lemma": "decide", "pos": "verb", "level": "A2", "translations": ["решать"]},
    {"lemma": "learn", "pos": "verb", "level": "A2", "translations": ["учиться"]},
    {"lemma": "lead", "pos": "verb", "level": "A2", "translations": ["вести"]},
    {"lemma": "provide", "pos": "verb", "level": "A2", "translations": ["предоставлять"]},
    {"lemma": "lose", "pos": "verb", "level": "A2", "translations": ["терять"]},
    {"lemma": "pay", "pos": "verb", "level": "A2", "translations": ["платить"]},
    {"lemma": "meet", "pos": "verb", "level": "A2", "translations": ["встречать"]},
    {"lemma": "include", "pos": "verb", "level": "A2", "translations": ["включать"]},
    {"lemma": "continue", "pos": "verb", "level": "A2", "translations": ["продолжать"]},
    {"lemma": "set", "pos": "verb", "level": "A2", "translations": ["устанавливать"]},
    {"lemma": "help", "pos": "verb", "level": "A2", "translations": ["помогать"]},
    {"lemma": "talk", "pos": "verb", "level": "A2", "translations": ["говорить"]},
    {"lemma": "turn", "pos": "verb", "level": "A2", "translations": ["поворачивать"]},
    {"lemma": "start", "pos": "verb", "level": "A2", "translations": ["начинать"]},
    {"lemma": "show", "pos": "verb", "level": "A2", "translations": ["показывать"]},
    {"lemma": "hear", "pos": "verb", "level": "A2", "translations": ["слышать"]},
    {"lemma": "play", "pos": "verb", "level": "A2", "translations": ["играть"]},
    {"lemma": "run", "pos": "verb", "level": "A2", "translations": ["бежать"]},
    {"lemma": "move", "pos": "verb", "level": "A2", "translations": ["двигаться"]},
    {"lemma": "like", "pos": "verb", "level": "A2", "translations": ["нравиться"]},
    {"lemma": "live", "pos": "verb", "level": "A2", "translations": ["жить"]},
    {"lemma": "believe", "pos": "verb", "level": "A2", "translations": ["верить"]},
    {"lemma": "hold", "pos": "verb", "level": "A2", "translations": ["держать"]},
    {"lemma": "bring", "pos": "verb", "level": "A2", "translations": ["приносить"]},
    {"lemma": "happen", "pos": "verb", "level": "A2", "translations": ["происходить"]},
    {"lemma": "write", "pos": "verb", "level": "A2", "translations": ["писать"]},
    {"lemma": "read", "pos": "verb", "level": "A2", "translations": ["читать"]},
    
    # Прилагательные A2
    {"lemma": "beautiful", "pos": "adjective", "level": "A2", "translations": ["красивый"]},
    {"lemma": "happy", "pos": "adjective", "level": "A2", "translations": ["счастливый"]},
    {"lemma": "sad", "pos": "adjective", "level": "A2", "translations": ["грустный"]},
    {"lemma": "easy", "pos": "adjective", "level": "A2", "translations": ["легкий"]},
    {"lemma": "difficult", "pos": "adjective", "level": "A2", "translations": ["трудный"]},
    {"lemma": "simple", "pos": "adjective", "level": "A2", "translations": ["простой"]},
    {"lemma": "fast", "pos": "adjective", "level": "A2", "translations": ["быстрый"]},
    {"lemma": "slow", "pos": "adjective", "level": "A2", "translations": ["медленный"]},
    {"lemma": "hot", "pos": "adjective", "level": "A2", "translations": ["горячий"]},
    {"lemma": "cold", "pos": "adjective", "level": "A2", "translations": ["холодный"]},
    {"lemma": "clean", "pos": "adjective", "level": "A2", "translations": ["чистый"]},
    {"lemma": "dirty", "pos": "adjective", "level": "A2", "translations": ["грязный"]},
    {"lemma": "strong", "pos": "adjective", "level": "A2", "translations": ["сильный"]},
    {"lemma": "weak", "pos": "adjective", "level": "A2", "translations": ["слабый"]},
    {"lemma": "rich", "pos": "adjective", "level": "A2", "translations": ["богатый"]},
    {"lemma": "poor", "pos": "adjective", "level": "A2", "translations": ["бедный"]},
    {"lemma": "full", "pos": "adjective", "level": "A2", "translations": ["полный"]},
    {"lemma": "empty", "pos": "adjective", "level": "A2", "translations": ["пустой"]},
    {"lemma": "open", "pos": "adjective", "level": "A2", "translations": ["открытый"]},
    {"lemma": "closed", "pos": "adjective", "level": "A2", "translations": ["закрытый"]},
    
    # B1 - Продвинутая базовая лексика
    {"lemma": "achieve", "pos": "verb", "level": "B1", "translations": ["достигать"]},
    {"lemma": "advantage", "pos": "noun", "level": "B1", "translations": ["преимущество"]},
    {"lemma": "behavior", "pos": "noun", "level": "B1", "translations": ["поведение"]},
    {"lemma": "challenge", "pos": "noun", "level": "B1", "translations": ["вызов"]},
    {"lemma": "character", "pos": "noun", "level": "B1", "translations": ["характер"]},
    {"lemma": "communication", "pos": "noun", "level": "B1", "translations": ["общение"]},
    {"lemma": "confidence", "pos": "noun", "level": "B1", "translations": ["уверенность"]},
    {"lemma": "connection", "pos": "noun", "level": "B1", "translations": ["связь"]},
    {"lemma": "consequence", "pos": "noun", "level": "B1", "translations": ["последствие"]},
    {"lemma": "contribute", "pos": "verb", "level": "B1", "translations": ["вносить вклад"]},
    {"lemma": "creative", "pos": "adjective", "level": "B1", "translations": ["творческий"]},
    {"lemma": "decision", "pos": "noun", "level": "B1", "translations": ["решение"]},
    {"lemma": "describe", "pos": "verb", "level": "B1", "translations": ["описывать"]},
    {"lemma": "despite", "pos": "preposition", "level": "B1", "translations": ["несмотря на"]},
    {"lemma": "determine", "pos": "verb", "level": "B1", "translations": ["определять"]},
    {"lemma": "effective", "pos": "adjective", "level": "B1", "translations": ["эффективный"]},
    {"lemma": "encourage", "pos": "verb", "level": "B1", "translations": ["поощрять"]},
    {"lemma": "environment", "pos": "noun", "level": "B1", "translations": ["окружающая среда"]},
    {"lemma": "establish", "pos": "verb", "level": "B1", "translations": ["устанавливать"]},
    {"lemma": "evaluate", "pos": "verb", "level": "B1", "translations": ["оценивать"]},
    {"lemma": "evidence", "pos": "noun", "level": "B1", "translations": ["доказательство"]},
    {"lemma": "experience", "pos": "noun", "level": "B1", "translations": ["опыт"]},
    {"lemma": "explain", "pos": "verb", "level": "B1", "translations": ["объяснять"]},
    {"lemma": "explore", "pos": "verb", "level": "B1", "translations": ["исследовать"]},
    {"lemma": "express", "pos": "verb", "level": "B1", "translations": ["выражать"]},
    {"lemma": "failure", "pos": "noun", "level": "B1", "translations": ["неудача"]},
    {"lemma": "feature", "pos": "noun", "level": "B1", "translations": ["особенность"]},
    {"lemma": "focus", "pos": "verb", "level": "B1", "translations": ["сосредоточиться"]},
    {"lemma": "generate", "pos": "verb", "level": "B1", "translations": ["генерировать"]},
    {"lemma": "goal", "pos": "noun", "level": "B1", "translations": ["цель"]},
    {"lemma": "identify", "pos": "verb", "level": "B1", "translations": ["идентифицировать"]},
    {"lemma": "improve", "pos": "verb", "level": "B1", "translations": ["улучшать"]},
    {"lemma": "independent", "pos": "adjective", "level": "B1", "translations": ["независимый"]},
    {"lemma": "influence", "pos": "noun", "level": "B1", "translations": ["влияние"]},
    {"lemma": "knowledge", "pos": "noun", "level": "B1", "translations": ["знание"]},
    {"lemma": "maintain", "pos": "verb", "level": "B1", "translations": ["поддерживать"]},
    {"lemma": "opportunity", "pos": "noun", "level": "B1", "translations": ["возможность"]},
    {"lemma": "participate", "pos": "verb", "level": "B1", "translations": ["участвовать"]},
    {"lemma": "perspective", "pos": "noun", "level": "B1", "translations": ["перспектива"]},
    {"lemma": "positive", "pos": "adjective", "level": "B1", "translations": ["позитивный"]},
    {"lemma": "potential", "pos": "noun", "level": "B1", "translations": ["потенциал"]},
    {"lemma": "prepare", "pos": "verb", "level": "B1", "translations": ["готовить"]},
    {"lemma": "pressure", "pos": "noun", "level": "B1", "translations": ["давление"]},
    {"lemma": "prevent", "pos": "verb", "level": "B1", "translations": ["предотвращать"]},
    {"lemma": "process", "pos": "noun", "level": "B1", "translations": ["процесс"]},
    {"lemma": "produce", "pos": "verb", "level": "B1", "translations": ["производить"]},
    {"lemma": "professional", "pos": "adjective", "level": "B1", "translations": ["профессиональный"]},
    {"lemma": "quality", "pos": "noun", "level": "B1", "translations": ["качество"]},
    {"lemma": "recognize", "pos": "verb", "level": "B1", "translations": ["признавать"]},
    {"lemma": "recommend", "pos": "verb", "level": "B1", "translations": ["рекомендовать"]},
    {"lemma": "reduce", "pos": "verb", "level": "B1", "translations": ["уменьшать"]},
    {"lemma": "reflect", "pos": "verb", "level": "B1", "translations": ["отражать"]},
    {"lemma": "relationship", "pos": "noun", "level": "B1", "translations": ["отношения"]},
    {"lemma": "require", "pos": "verb", "level": "B1", "translations": ["требовать"]},
    {"lemma": "respond", "pos": "verb", "level": "B1", "translations": ["отвечать"]},
    {"lemma": "responsible", "pos": "adjective", "level": "B1", "translations": ["ответственный"]},
    {"lemma": "significant", "pos": "adjective", "level": "B1", "translations": ["значительный"]},
    {"lemma": "similar", "pos": "adjective", "level": "B1", "translations": ["похожий"]},
    {"lemma": "situation", "pos": "noun", "level": "B1", "translations": ["ситуация"]},
    {"lemma": "skill", "pos": "noun", "level": "B1", "translations": ["навык"]},
    {"lemma": "solution", "pos": "noun", "level": "B1", "translations": ["решение"]},
    {"lemma": "specific", "pos": "adjective", "level": "B1", "translations": ["специфический"]},
    {"lemma": "strategy", "pos": "noun", "level": "B1", "translations": ["стратегия"]},
    {"lemma": "structure", "pos": "noun", "level": "B1", "translations": ["структура"]},
    {"lemma": "success", "pos": "noun", "level": "B1", "translations": ["успех"]},
    {"lemma": "support", "pos": "verb", "level": "B1", "translations": ["поддерживать"]},
    {"lemma": "traditional", "pos": "adjective", "level": "B1", "translations": ["традиционный"]},
    {"lemma": "transfer", "pos": "verb", "level": "B1", "translations": ["передавать"]},
    {"lemma": "understand", "pos": "verb", "level": "B1", "translations": ["понимать"]},
    {"lemma": "valuable", "pos": "adjective", "level": "B1", "translations": ["ценный"]},
    {"lemma": "variety", "pos": "noun", "level": "B1", "translations": ["разнообразие"]},
]


async def create_general_dictionary():
    """Создаем словарь широкой тематики"""
    async with async_session_factory() as session:
        # Проверяем, существует ли уже словарь
        result = await session.execute(
            select(Dictionary).where(Dictionary.name == "Общий словарь")
        )
        existing_dict = result.scalar_one_or_none()
        
        if existing_dict:
            print(f"⚠️  Словарь 'Общий словарь' уже существует (id={existing_dict.id})")
            print(f"   Пропускаем создание.")
            return
        
        # Создаем новый словарь
        dictionary = Dictionary(
            name="Общий словарь",
            description="Базовая лексика широкой тематики для повседневного общения",
            category="general"
        )
        session.add(dictionary)
        await session.flush()
        
        print(f"✅ Создан словарь 'Общий словарь' (id={dictionary.id})")
        print(f"   Описание: {dictionary.description}")
        print(f"   Категория: {dictionary.category}")
        
        # Добавляем слова
        added_count = 0
        skipped_count = 0
        
        for word_data in GENERAL_WORDS:
            lemma_key = make_lemma_key(word_data["lemma"])
            
            # Проверяем, существует ли слово
            result = await session.execute(
                select(Word).where(
                    Word.lemma_key == lemma_key,
                    Word.pos == word_data["pos"]
                )
            )
            word = result.scalar_one_or_none()
            
            # Создаем слово, если его нет
            if not word:
                word = Word(
                    lemma=word_data["lemma"],
                    lemma_key=lemma_key,
                    pos=word_data["pos"],
                    level=word_data["level"],
                    translations=word_data["translations"]
                )
                session.add(word)
                await session.flush()
                added_count += 1
            
            # Проверяем, есть ли уже связь
            result = await session.execute(
                select(DictionaryWord).where(
                    DictionaryWord.dictionary_id == dictionary.id,
                    DictionaryWord.word_id == word.id
                )
            )
            if not result.scalar_one_or_none():
                # Создаем связь
                link = DictionaryWord(
                    dictionary_id=dictionary.id,
                    word_id=word.id
                )
                session.add(link)
            else:
                skipped_count += 1
        
        await session.commit()
        
        print(f"\n📊 Статистика:")
        print(f"   Всего слов в списке: {len(GENERAL_WORDS)}")
        print(f"   Добавлено новых слов: {added_count}")
        print(f"   Пропущено (уже были в словаре): {skipped_count}")
        
        # Подсчитываем итоговое количество слов в словаре
        result = await session.execute(
            select(DictionaryWord).where(DictionaryWord.dictionary_id == dictionary.id)
        )
        total_words = len(result.scalars().all())
        
        print(f"\n✅ Готово!")
        print(f"   Словарь 'Общий словарь' содержит {total_words} слов")
        print(f"\n💡 Теперь пользователи могут выбрать этот словарь в настройках")


if __name__ == "__main__":
    print("🚀 Создание словаря широкой тематики...")
    print("=" * 60)
    asyncio.run(create_general_dictionary())
