from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, Dictionary, Word, Lesson, LearningProfile
from schemas import DictionaryImportRequest, DictionaryImportResponse
from auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/dictionaries/import", response_model=DictionaryImportResponse)
async def import_dictionary(
    body: DictionaryImportRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Import words into a dictionary.
    Supports dry_run mode and batch upsert up to 1000 rows.
    """
    if len(body.words) > 1000:
        raise HTTPException(status_code=400, detail="Max 1000 words per batch")

    # Check dictionary exists
    result = await db.execute(select(Dictionary).where(Dictionary.id == body.dictionary_id))
    dictionary = result.scalar_one_or_none()
    if not dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    created = 0
    updated = 0
    errors = []

    for word_data in body.words:
        try:
            lemma = word_data.get("lemma", "").strip()
            pos = word_data.get("pos", "").strip()
            level = word_data.get("level", "").strip()
            translations = word_data.get("translations", [])

            if not lemma or not pos or not level:
                errors.append(f"Missing required fields: {word_data}")
                continue

            # Calculate lemma_key
            import unicodedata
            lemma_key = unicodedata.normalize("NFC", lemma).casefold().strip()

            # Check existing
            result = await db.execute(
                select(Word).where(
                    Word.lemma_key == lemma_key,
                    Word.pos == pos,
                    Word.dictionary_id == body.dictionary_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                if not body.dry_run:
                    existing.lemma = lemma
                    existing.translations = translations
                    existing.level = level
                updated += 1
            else:
                if not body.dry_run:
                    word = Word(
                        lemma=lemma,
                        lemma_key=lemma_key,
                        pos=pos,
                        level=level,
                        translations=translations,
                        dictionary_id=body.dictionary_id,
                    )
                    db.add(word)
                created += 1

        except Exception as e:
            errors.append(f"Error processing {word_data}: {str(e)}")

    if not body.dry_run:
        await db.flush()

    return DictionaryImportResponse(
        total=len(body.words),
        created=created,
        updated=updated,
        errors=errors,
    )


@router.get("/reports/summary")
async def get_admin_report(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get admin summary report."""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Total lessons
    result = await db.execute(select(func.count(Lesson.id)))
    total_lessons = result.scalar() or 0

    # Active profiles
    result = await db.execute(select(func.count(LearningProfile.id)))
    total_profiles = result.scalar() or 0

    return {
        "total_users": total_users,
        "total_lessons": total_lessons,
        "total_profiles": total_profiles,
    }
