"""
GigaChat API client using official SDK.

Согласно документации: https://developers.sber.ru/docs/ru/gigachat/api/main

SDK автоматически:
- Получает и обновляет токен доступа
- Кэширует токен
- Обновляет токен за 60 секунд до истечения
"""

import asyncio
import json
import time
import secrets
import logging
from typing import Optional, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from config import settings
from models import LLMCall

logger = logging.getLogger(__name__)


class GigaChatClient:
    """Client for GigaChat API using official SDK."""

    def __init__(self):
        self._giga = None
        self._lock = asyncio.Lock()

    async def _get_client(self):
        """Get or create GigaChat client (singleton with thread safety)."""
        async with self._lock:
            if self._giga is None:
                try:
                    from gigachat import GigaChat
                    
                    # Проверка credentials
                    if not settings.GIGACHAT_AUTH_KEY:
                        raise Exception(
                            "GigaChat credentials not configured. "
                            "Set GIGACHAT_AUTH_KEY in backend/.env"
                        )
                    
                    logger.info("🔑 Initializing GigaChat SDK...")
                    logger.info(f"   Base URL: https://api.giga.chat/v1")
                    logger.info(f"   Auth Key preview: {settings.GIGACHAT_AUTH_KEY[:30]}...")
                    
                    # Создаём клиент с официальным SDK
                    # SDK сам управляет токенами
                    self._giga = GigaChat(
                        credentials=settings.GIGACHAT_AUTH_KEY,
                        scope="GIGACHAT_API_PERS",
                        model="GigaChat-3-Ultra",  # Используем GigaChat-3-Ultra
                        verify_ssl_certs=False,  # Для тестирования (в production нужен сертификат НУЦ)
                    )
                    
                    logger.info("✅ GigaChat SDK initialized successfully")
                    
                except ImportError:
                    logger.error("❌ gigachat package not installed!")
                    logger.error("   Run: pip install gigachat")
                    raise
                except Exception as e:
                    logger.error(f"❌ Failed to initialize GigaChat: {e}")
                    raise
            
            return self._giga

    async def _call_llm(
        self,
        prompt: str,
        temperature: float,
        purpose: str,
        db: AsyncSession,
        user_id: int | None = None,
        lesson_id: int | None = None,
        max_retries: int = 2,
    ) -> dict:
        """Make LLM call with retry logic and logging."""
        start_time = time.time()
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                giga = await self._get_client()
                
                logger.info(f"🤖 Calling GigaChat API (attempt {attempt + 1}/{max_retries + 1})")
                logger.info(f"   Purpose: {purpose}")
                logger.info(f"   Temperature: {temperature}")
                logger.info(f"   Prompt length: {len(prompt)} chars")
                
                # Импортируем модели SDK
                from gigachat.models import Chat, Messages
                
                # Отправляем запрос через SDK
                response = giga.chat(
                    Chat(
                        model="GigaChat-3-Ultra",  # Явно указываем модель
                        messages=[
                            Messages(role="system", content="You are a helpful language teaching assistant. Always respond with valid JSON only, no markdown."),
                            Messages(role="user", content=prompt),
                        ],
                        temperature=temperature,
                        max_tokens=2000,
                    )
                )

                latency_ms = int((time.time() - start_time) * 1000)
                
                # Логируем структуру ответа для отладки
                logger.info(f"📊 Response received")
                logger.info(f"   Response type: {type(response).__name__}")
                
                # Извлекаем контент из ответа
                try:
                    if hasattr(response, 'choices') and len(response.choices) > 0:
                        content = response.choices[0].message.content
                        logger.info(f"   Content length: {len(content)} chars")
                    else:
                        raise ValueError("Response has no choices")
                    
                    tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else None
                    logger.info(f"   Tokens: {tokens}")
                except Exception as e:
                    logger.error(f"❌ Failed to parse response: {e}")
                    logger.error(f"   Response: {response}")
                    raise

                logger.info(f"✅ GigaChat response received")
                logger.info(f"   Latency: {latency_ms}ms")
                logger.info(f"   Tokens: {tokens}")
                logger.info(f"   Response length: {len(content)} chars")

                # Parse JSON
                logger.info(f"📝 Raw content from LLM:\n{content[:500]}...")
                try:
                    result = self._parse_json_response(content)
                    logger.info(f"✅ JSON parsed successfully")
                    logger.info(f"   Result type: {type(result)}")
                    logger.info(f"   Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
                except Exception as e:
                    logger.error(f"❌ Failed to parse JSON: {e}")
                    logger.error(f"   Content that failed to parse:\n{content}")
                    raise

                await self._log_call(db, purpose, user_id, lesson_id, prompt, result, "success", latency_ms, tokens)
                return result

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ GigaChat call failed (attempt {attempt + 1}): {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                logger.error(f"   Error message: {str(e)}")
                import traceback
                logger.error(f"   Full traceback:\n{traceback.format_exc()}")
                
                if attempt < max_retries:
                    logger.info(f"   Retrying in 1 second...")
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.error(f"   All retries exhausted")

        latency_ms = int((time.time() - start_time) * 1000)
        await self._log_call(db, purpose, user_id, lesson_id, prompt, None, "error", latency_ms, None)
        raise Exception(f"LLM call failed after {max_retries + 1} attempts: {last_error}")

    def _parse_json_response(self, content: str) -> dict | list:
        """Parse and validate JSON from LLM response."""
        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        return json.loads(content)

    async def _log_call(
        self,
        db: AsyncSession,
        purpose: str,
        user_id: int | None,
        lesson_id: int | None,
        request_data: Any,
        response_data: Any,
        status: str,
        latency_ms: int,
        tokens: int | None,
    ):
        """Log LLM call to database."""
        try:
            await db.execute(
                insert(LLMCall).values(
                    purpose=purpose,
                    user_id=user_id,
                    lesson_id=lesson_id,
                    request={"prompt": str(request_data)[:5000]},
                    response={"data": str(response_data)[:5000]} if response_data else None,
                    status=status,
                    latency_ms=latency_ms,
                    tokens=tokens,
                )
            )
            await db.flush()
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")

    async def generate_exercises(
        self,
        word_clusters: list[dict],
        level: str,
        db: AsyncSession,
        user_id: int | None = None,
        lesson_id: int | None = None,
    ) -> list[dict]:
        """Generate exercises for word clusters (Prompt 1). Temperature 0.7."""
        prompt = _build_exercise_prompt(word_clusters, level)

        for attempt in range(3):  # max 2 retries = 3 attempts
            result = await self._call_llm(
                prompt=prompt,
                temperature=0.7,
                purpose="generate_exercise",
                db=db,
                user_id=user_id,
                lesson_id=lesson_id,
                max_retries=2,
            )

            # Validate
            if self._validate_exercise_response(result, word_clusters):
                return result

            logger.warning(f"Invalid exercise response, attempt {attempt + 1}")

        raise Exception("Failed to generate valid exercises after 3 attempts")

    def _validate_exercise_response(self, result: list, word_clusters: list[dict]) -> bool:
        """Validate exercise generation response."""
        if not isinstance(result, list):
            return False
        if len(result) != len(word_clusters):
            return False

        for item in result:
            if not isinstance(item, dict):
                return False
            if "sentence" not in item or "reference_translation" not in item:
                return False

            sentence = item["sentence"]
            translation = item["reference_translation"]

            # No Cyrillic in English sentence
            if any('\u0400' <= c <= '\u04FF' for c in sentence):
                return False

            # Must have Cyrillic in translation
            if not any('\u0400' <= c <= '\u04FF' for c in translation):
                return False

            # Length checks
            if len(sentence) > 200 or len(translation) > 300:
                return False

        return True

    async def evaluate_translation(
        self,
        target_sentence: str,
        user_translation: str,
        target_words: list[dict],
        db: AsyncSession,
        user_id: int | None = None,
        lesson_id: int | None = None,
    ) -> dict:
        """Evaluate user translation (Prompt 2). Temperature 0.2."""
        prompt = _build_evaluate_prompt(
            target_sentence, user_translation, target_words
        )
        
        logger.info(f"🔍 Evaluate translation request:")
        logger.info(f"   Target sentence: {target_sentence}")
        logger.info(f"   User translation: {user_translation}")
        logger.info(f"   Target words: {[w['lemma'] for w in target_words]}")
        logger.info(f"   Prompt length: {len(prompt)} chars")

        for attempt in range(2):  # max 1 retry
            logger.info(f"🔄 Evaluate attempt {attempt + 1}/2")
            try:
                result = await self._call_llm(
                    prompt=prompt,
                    temperature=0.2,
                    purpose="evaluate_translation",
                    db=db,
                    user_id=user_id,
                    lesson_id=lesson_id,
                    max_retries=2,
                )
                
                logger.info(f"📥 LLM raw response: {result}")

                if self._validate_evaluate_response(result, target_words):
                    logger.info(f"✅ Response validated successfully")
                    return result
                else:
                    logger.warning(f"❌ Response validation failed")
                    logger.warning(f"   Response type: {type(result)}")
                    logger.warning(f"   Response keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
                    logger.warning(f"   Full response: {result}")
            except Exception as e:
                logger.error(f"❌ LLM call failed on attempt {attempt + 1}: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback:\n{traceback.format_exc()}")
                if attempt == 1:  # last attempt
                    raise

        raise Exception("Failed to evaluate translation after 2 attempts")

    def _validate_evaluate_response(self, result: dict, target_words: list[dict]) -> bool:
        """Validate evaluation response."""
        logger.info(f"🔍 Validating LLM response...")
        
        if not isinstance(result, dict):
            logger.warning(f"   ❌ Result is not a dict: {type(result)}")
            return False
        
        if "evaluations" not in result:
            logger.warning(f"   ❌ Missing 'evaluations' key. Keys: {result.keys()}")
            return False
            
        if "overall_result" not in result:
            logger.warning(f"   ❌ Missing 'overall_result' key. Keys: {result.keys()}")
            return False
            
        if result["overall_result"] not in ("correct", "typo", "incorrect"):
            logger.warning(f"   ❌ Invalid overall_result: {result['overall_result']}")
            return False
            
        if not isinstance(result["evaluations"], list):
            logger.warning(f"   ❌ 'evaluations' is not a list: {type(result['evaluations'])}")
            return False
            
        if "new_suggested_words" not in result:
            logger.warning(f"   ❌ Missing 'new_suggested_words' key. Keys: {result.keys()}")
            return False
            
        if not isinstance(result["new_suggested_words"], list):
            logger.warning(f"   ❌ 'new_suggested_words' is not a list: {type(result['new_suggested_words'])}")
            return False

        for i, ev in enumerate(result["evaluations"]):
            if not isinstance(ev, dict):
                logger.warning(f"   ❌ Evaluation {i} is not a dict: {type(ev)}")
                return False
            if ev.get("result") not in ("correct", "typo", "incorrect"):
                logger.warning(f"   ❌ Evaluation {i} has invalid result: {ev.get('result')}")
                return False
            if "word_lemma" not in ev:
                logger.warning(f"   ❌ Evaluation {i} missing 'word_lemma'")
                return False
            if "user_fragment" not in ev:
                logger.warning(f"   ❌ Evaluation {i} missing 'user_fragment'")
                return False

        logger.info(f"   ✅ Validation passed")
        return True


def _wrap_user_input(text: str) -> str:
    """Protect against prompt injection."""
    tag = secrets.token_hex(4)
    return f"<<<UT_{tag}>>>{text}<<<UT_{tag}>>>"


def _build_exercise_prompt(
    word_clusters: list[dict],
    level: str,
) -> str:
    """
    Build prompt for exercise generation from template file.
    word_clusters: [{"words": [{"lemma": ..., "pos": ..., "translations": [...]}]}]
    """
    import os
    
    # Read prompt template from file
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'generate_exercise.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Format clusters
    clusters_text = ""
    for i, cluster in enumerate(word_clusters):
        words_text = ", ".join(
            f"{w['lemma']} ({w['pos']}) = {', '.join(w['translations'])}"
            for w in cluster["words"]
        )
        clusters_text += f"Группа {i+1}: {words_text}\n"
    
    # Substitute variables in template
    prompt = prompt_template.format(
        level=level,
        clusters_text=clusters_text
    )
    
    return prompt


def _build_evaluate_prompt(
    target_sentence: str,
    user_translation: str,
    target_words: list[dict],
) -> str:
    """
    Build prompt for translation evaluation from template file.
    """
    import os
    
    # Read prompt template from file
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'evaluate_translation.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Format target words
    words_text = ", ".join(
        f"{w['lemma']} ({', '.join(w['translations'])})"
        for w in target_words
    )
    
    # Wrap user input for injection protection
    wrapped_user = _wrap_user_input(user_translation)
    
    # Substitute variables in template
    prompt = prompt_template.format(
        target_sentence=target_sentence,
        wrapped_user=wrapped_user,
        words_text=words_text
    )
    
    return prompt


# Singleton
gigachat_client = GigaChatClient()
