from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Index,
    UniqueConstraint, Text, Float, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    timezone = Column(String(64), nullable=False, default="Europe/Moscow")
    is_onboarded = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    profile = relationship("LearningProfile", back_populates="user", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    llm_calls = relationship("LLMCall", back_populates="user")


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    level = Column(String(2), nullable=False)  # A1, A2, B1, B2
    dictionary_id = Column(Integer, ForeignKey("dictionaries.id"), nullable=True)
    daily_lesson_limit = Column(Integer, nullable=False, default=5)
    last_lesson_number = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
    dictionary = relationship("Dictionary")
    user_words = relationship("UserWord", back_populates="profile", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="profile", cascade="all, delete-orphan")


class Dictionary(Base):
    __tablename__ = "dictionaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    words = relationship("Word", back_populates="dictionary")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    lemma = Column(String(255), nullable=False)
    lemma_key = Column(String(255), nullable=False)
    pos = Column(String(32), nullable=False)  # part of speech
    level = Column(String(2), nullable=False)
    translations = Column(JSONB, nullable=False, default=[])
    dictionary_id = Column(Integer, ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    dictionary = relationship("Dictionary", back_populates="words")

    __table_args__ = (
        UniqueConstraint("lemma_key", "pos", name="uq_words_lemma_pos"),
        Index("ix_words_dictionary_level", "dictionary_id", "level"),
    )


class UserWord(Base):
    __tablename__ = "user_words"

    id = Column(Integer, primary_key=True, index=True)
    learning_profile_id = Column(Integer, ForeignKey("learning_profiles.id", ondelete="CASCADE"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(16), nullable=False, default="active")  # active, mastered, ignored
    stage = Column(Integer, nullable=False, default=0)  # 0-6
    due_lesson_number = Column(Integer, nullable=True)  # NULL when mastered
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    profile = relationship("LearningProfile", back_populates="user_words")
    word = relationship("Word")

    __table_args__ = (
        UniqueConstraint("learning_profile_id", "word_id", name="uq_user_words_profile_word"),
        Index("ix_user_words_due", "learning_profile_id", "due_lesson_number"),
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    learning_profile_id = Column(Integer, ForeignKey("learning_profiles.id", ondelete="CASCADE"), nullable=False)
    lesson_number = Column(Integer, nullable=False)
    status = Column(String(16), nullable=False, default="in_progress")  # in_progress, completed, abandoned
    started_local_date = Column(String(10), nullable=False)  # YYYY-MM-DD in user timezone
    completed_local_date = Column(String(10), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    profile = relationship("LearningProfile", back_populates="lessons")
    exercises = relationship("LessonExercise", back_populates="lesson", cascade="all, delete-orphan", order_by="LessonExercise.order_index")

    __table_args__ = (
        UniqueConstraint("learning_profile_id", "lesson_number", name="uq_lessons_profile_number"),
        # Partial unique index: only one in_progress per profile
        Index(
            "uq_lessons_in_progress",
            "learning_profile_id",
            unique=True,
            postgresql_where=func.text_column("status") == "in_progress",
        ),
    )


class LessonExercise(Base):
    __tablename__ = "lesson_exercises"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False)
    target_sentence = Column(Text, nullable=False)
    reference_translation = Column(Text, nullable=False)
    user_translation = Column(Text, nullable=True)
    status = Column(String(16), nullable=False, default="pending")  # pending, evaluated
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    lesson = relationship("Lesson", back_populates="exercises")
    exercise_words = relationship("LessonExerciseWord", back_populates="exercise", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("lesson_id", "order_index", name="uq_exercises_lesson_order"),
    )


class LessonExerciseWord(Base):
    __tablename__ = "lesson_exercise_words"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("lesson_exercises.id", ondelete="CASCADE"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    is_target = Column(Boolean, nullable=False, default=True)
    is_new = Column(Boolean, nullable=False, default=False)
    surface_form = Column(String(255), nullable=False)
    result = Column(String(16), nullable=True)  # correct, typo, incorrect, dont_know
    user_fragment = Column(String(255), nullable=True)
    stage_before = Column(Integer, nullable=False, default=0)
    stage_after = Column(Integer, nullable=False, default=0)

    exercise = relationship("LessonExercise", back_populates="exercise_words")
    word = relationship("Word")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    family_id = Column(String(64), nullable=False, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")


class LLMCall(Base):
    __tablename__ = "llm_calls"

    id = Column(Integer, primary_key=True, index=True)
    purpose = Column(String(64), nullable=False)  # generate_exercise, evaluate_translation
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    request = Column(JSONB, nullable=False)
    response = Column(JSONB, nullable=True)
    status = Column(String(16), nullable=False)  # success, error, timeout
    latency_ms = Column(Integer, nullable=True)
    tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="llm_calls")

    __table_args__ = (
        Index("ix_llm_calls_created", "created_at"),
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(64), nullable=False, index=True)  # signup, lesson_started, lesson_completed, exercise_evaluated, llm_error
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
