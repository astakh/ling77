from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, Dictionary, Word, Lesson, LearningProfile, DictionaryWord
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

            # Check if word exists (globally by lemma_key + pos)
            result = await db.execute(
                select(Word).where(
                    Word.lemma_key == lemma_key,
                    Word.pos == pos,
                )
            )
            existing_word = result.scalar_one_or_none()

            if existing_word:
                # Word exists - check if it's already in this dictionary
                link_result = await db.execute(
                    select(DictionaryWord).where(
                        DictionaryWord.dictionary_id == body.dictionary_id,
                        DictionaryWord.word_id == existing_word.id,
                    )
                )
                existing_link = link_result.scalar_one_or_none()
                
                if existing_link:
                    # Already linked - update word data
                    if not body.dry_run:
                        existing_word.lemma = lemma
                        existing_word.translations = translations
                        existing_word.level = level
                    updated += 1
                else:
                    # Word exists but not in this dictionary - add link
                    if not body.dry_run:
                        link = DictionaryWord(
                            dictionary_id=body.dictionary_id,
                            word_id=existing_word.id,
                        )
                        db.add(link)
                    updated += 1
            else:
                # New word - create it and link to dictionary
                if not body.dry_run:
                    word = Word(
                        lemma=lemma,
                        lemma_key=lemma_key,
                        pos=pos,
                        level=level,
                        translations=translations,
                    )
                    db.add(word)
                    await db.flush()  # Get word.id
                    
                    link = DictionaryWord(
                        dictionary_id=body.dictionary_id,
                        word_id=word.id,
                    )
                    db.add(link)
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
