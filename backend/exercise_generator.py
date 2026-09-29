"""
Fallback exercise generator - generates exercises without LLM.
Used when GigaChat API is not available or not configured.
"""

import random
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


# Pre-defined sentence templates for different word types
SENTENCE_TEMPLATES = {
    "noun": [
        "The {word} is very important.",
        "I see a {word} every day.",
        "This {word} belongs to me.",
        "The {word} looks beautiful.",
        "I need a {word} right now.",
    ],
    "verb": [
        "I {word} every morning.",
        "She likes to {word} in the park.",
        "We should {word} together.",
        "They {word} very quickly.",
        "He wants to {word} today.",
    ],
    "adjective": [
        "The {word} house is old.",
        "This {word} book is interesting.",
        "She has a {word} smile.",
        "The weather is {word} today.",
        "It was a {word} experience.",
    ],
    "adverb": [
        "She sings {word}.",
        "He runs {word} every day.",
        "They work {word} together.",
        "The car moves {word}.",
        "Please speak {word}.",
    ],
}

# Russian translations for templates
TRANSLATION_TEMPLATES = {
    "noun": [
        "{word_translation} очень важен.",
        "Я вижу {word_translation} каждый день.",
        "Этот {word_translation} принадлежит мне.",
        "{word_translation} выглядит красиво.",
        "Мне нужен {word_translation} прямо сейчас.",
    ],
    "verb": [
        "Я {word_translation} каждое утро.",
        "Она любит {word_translation} в парке.",
        "Мы должны {word_translation} вместе.",
        "Они {word_translation} очень быстро.",
        "Он хочет {word_translation} сегодня.",
    ],
    "adjective": [
        "{word_translation} дом старый.",
        "Эта {word_translation} книга интересная.",
        "У неё {word_translation} улыбка.",
        "Погода сегодня {word_translation}.",
        "Это был {word_translation} опыт.",
    ],
    "adverb": [
        "Она поёт {word_translation}.",
        "Он {word_translation} бегает каждый день.",
        "Они {word_translation} работают вместе.",
        "Машина движется {word_translation}.",
        "Пожалуйста, говорите {word_translation}.",
    ],
}


def generate_exercise_for_cluster(cluster: Dict, level: str) -> Dict:
    """
    Generate a single exercise for a word cluster without LLM.
    
    Args:
        cluster: Dictionary with "words" list containing word data
        level: User's language level (A1, A2, B1, B2)
    
    Returns:
        Dictionary with "sentence" and "reference_translation"
    """
    words = cluster["words"]
    
    if not words:
        return {
            "sentence": "Translate this sentence.",
            "reference_translation": "Переведите это предложение.",
        }
    
    # Use the first word as the main word for the sentence
    main_word = words[0]
    lemma = main_word["lemma"]
    pos = main_word["pos"]
    translations = main_word["translations"]
    
    # Get templates for this part of speech
    sentence_templates = SENTENCE_TEMPLATES.get(pos, SENTENCE_TEMPLATES["noun"])
    translation_templates = TRANSLATION_TEMPLATES.get(pos, TRANSLATION_TEMPLATES["noun"])
    
    # Select random templates
    sentence_template = random.choice(sentence_templates)
    translation_template = random.choice(translation_templates)
    
    # Generate sentence
    sentence = sentence_template.format(word=lemma)
    
    # Generate translation
    first_translation = translations[0] if translations else lemma
    reference_translation = translation_template.format(word_translation=first_translation)
    
    # If there are multiple words in the cluster, add them to the sentence
    if len(words) > 1:
        additional_words = []
        for word in words[1:]:
            additional_words.append(word["lemma"])
        
        # Add additional words to the sentence
        if pos == "noun":
            sentence = f"The {lemma} and {', '.join(additional_words)} are important."
            reference_translation = f"{first_translation} и {', '.join(w['translations'][0] if w['translations'] else w['lemma'] for w in words[1:])} важны."
        elif pos == "verb":
            sentence = f"I {lemma} and {', '.join(additional_words)} every day."
            reference_translation = f"Я {first_translation} и {', '.join(w['translations'][0] if w['translations'] else w['lemma'] for w in words[1:])} каждый день."
        else:
            sentence = f"The {lemma} is {', '.join(additional_words)}."
            reference_translation = f"{first_translation} - это {', '.join(w['translations'][0] if w['translations'] else w['lemma'] for w in words[1:])}."
    
    return {
        "sentence": sentence,
        "reference_translation": reference_translation,
    }


def generate_exercises_fallback(word_clusters: List[Dict], level: str) -> List[Dict]:
    """
    Generate exercises for all clusters without LLM.
    
    Args:
        word_clusters: List of clusters, each containing "words" list
        level: User's language level
    
    Returns:
        List of exercise dictionaries with "sentence" and "reference_translation"
    """
    logger.info(f"Generating {len(word_clusters)} exercises using fallback (no LLM)")
    
    results = []
    for cluster in word_clusters:
        exercise = generate_exercise_for_cluster(cluster, level)
        results.append(exercise)
    
    return results


def _fallback_evaluate_translation(
    user_translation: str,
    reference_translation: str,
    target_words: List[Dict]
) -> tuple[str, List[Dict]]:
    """
    Fallback translation evaluation without LLM.
    Uses simple keyword matching to evaluate the translation.
    
    Args:
        user_translation: User's Russian translation
        reference_translation: Correct Russian translation
        target_words: List of target words with their translations
    
    Returns:
        Tuple of (overall_result, evaluations)
        - overall_result: "correct", "typo", or "incorrect"
        - evaluations: List of evaluation dicts for each word
    """
    user_lower = user_translation.lower().strip()
    reference_lower = reference_translation.lower().strip()
    
    evaluations = []
    all_correct = True
    has_typo = False
    
    for word_data in target_words:
        lemma = word_data["lemma"]
        translations = word_data.get("translations", [])
        
        # Check if any translation appears in user's input
        found = False
        is_typo = False
        
        for translation in translations:
            translation_lower = translation.lower().strip()
            
            # Exact match
            if translation_lower in user_lower:
                found = True
                break
            
            # Check for typos (Levenshtein distance <= 2 for short words, <= 3 for longer)
            # Simple approach: check if most characters match
            if len(translation_lower) > 3:
                # Check if user translation contains a similar word
                user_words = user_lower.split()
                for user_word in user_words:
                    if _similar_words(user_word, translation_lower):
                        found = True
                        is_typo = True
                        break
            
            if found:
                break
        
        if found:
            if is_typo:
                result = "typo"
                has_typo = True
            else:
                result = "correct"
        else:
            result = "incorrect"
            all_correct = False
        
        evaluations.append({
            "word_lemma": lemma,
            "result": result,
            "user_fragment": translation_lower if found else "",
        })
    
    # Determine overall result
    if all_correct:
        overall_result = "correct"
    elif has_typo:
        overall_result = "typo"
    else:
        overall_result = "incorrect"
    
    return overall_result, evaluations


def _similar_words(word1: str, word2: str, max_distance: int = 2) -> bool:
    """
    Simple similarity check between two words.
    Returns True if words are similar (within max_distance edits).
    """
    # Remove punctuation
    word1 = ''.join(c for c in word1 if c.isalpha())
    word2 = ''.join(c for c in word2 if c.isalpha())
    
    if not word1 or not word2:
        return False
    
    # Length difference check
    if abs(len(word1) - len(word2)) > max_distance:
        return False
    
    # Simple character-by-character comparison
    matches = sum(1 for c1, c2 in zip(word1, word2) if c1 == c2)
    similarity = matches / max(len(word1), len(word2))
    
    # Consider similar if 70%+ characters match
    return similarity >= 0.7
