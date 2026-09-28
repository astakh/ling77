from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


# ============ Auth ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    timezone: str
    is_onboarded: bool
    is_admin: bool


class RefreshRequest(BaseModel):
    refresh_token: str


# ============ Onboarding ============

class OnboardingRequest(BaseModel):
    timezone: str = Field(pattern=r"^[A-Za-z]+/[A-Za-z_]+$")
    level: Literal["A1", "A2", "B1", "B2"]


# ============ Dashboard ============

class DashboardSummary(BaseModel):
    cta: Literal["start", "resume", "limit_reached"]
    streak: int
    total_lessons: int
    total_words: int
    mastered_words: int
    due_words: int
    lessons_today: int
    current_lesson_id: Optional[int] = None


# ============ Lesson ============

class LessonPreviewWord(BaseModel):
    id: int
    lemma: str
    translations: list[str]
    is_new: bool
    is_due: bool


class LessonPreviewResponse(BaseModel):
    words: list[LessonPreviewWord]


class DeclineWordRequest(BaseModel):
    word_id: int


class LessonStartRequest(BaseModel):
    idempotency_key: Optional[str] = None


class LessonStartResponse(BaseModel):
    lesson_id: int
    lesson_number: int
    exercises: list["ExerciseResponse"]


class ExerciseResponse(BaseModel):
    id: int
    order_index: int
    target_sentence: str
    reference_translation: str
    status: str
    words: list["ExerciseWordResponse"]


class ExerciseWordResponse(BaseModel):
    word_id: int
    is_target: bool
    is_new: bool
    surface_form: str
    result: Optional[str] = None
    stage_before: int
    stage_after: int


class EvaluateRequest(BaseModel):
    exercise_id: int
    user_translation: str
    idempotency_key: Optional[str] = None


class EvaluateResponse(BaseModel):
    exercise_id: int
    result: Literal["correct", "typo", "incorrect"]
    words: list["ExerciseWordResponse"]
    reference_translation: str
    is_last: bool


class LessonSummaryResponse(BaseModel):
    lesson_id: int
    lesson_number: int
    accuracy: int
    correct_count: int
    typo_count: int
    incorrect_count: int
    new_words_learned: int
    words_reviewed: int
    streak: int
    words: list[dict]


class DontKnowRequest(BaseModel):
    exercise_id: int


# ============ Vocabulary ============

class VocabularyWord(BaseModel):
    id: int
    word_id: int
    lemma: str
    pos: str
    translations: list[str]
    status: str
    stage: int
    due_lesson_number: Optional[int] = None


class VocabularyListResponse(BaseModel):
    words: list[VocabularyWord]
    total: int
    page: int
    page_size: int


class UpdateWordStatusRequest(BaseModel):
    status: Literal["active", "ignored", "mastered"]


# ============ Dictionaries ============

class DictionaryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str = "general"
    total_words: int
    levels: list[str]  # Levels of words IN this dictionary (not the dictionary's level)
    level_counts: dict[str, int]
    created_at: datetime


class DictionaryDetailResponse(DictionaryResponse):
    sample_words: list[dict]


class DictionaryListResponse(BaseModel):
    dictionaries: list[DictionaryResponse]


class DictionaryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class ChangeDictionaryRequest(BaseModel):
    dictionary_id: int


# ============ Admin ============

class DictionaryImportRequest(BaseModel):
    dictionary_id: int
    words: list[dict]
    dry_run: bool = True


class DictionaryImportResponse(BaseModel):
    total: int
    created: int
    updated: int
    errors: list[str]
