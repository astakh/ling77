"""
Admin routes for dictionary management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional

from database import get_db, async_session_factory
from models import Dictionary, Word, DictionaryWord
from config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None


class DictionaryListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    words_count: int


class DictionaryDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str


class WordInDictionaryResponse(BaseModel):
    id: int
    lemma: str
    pos: str
    level: str
    translations: list[str]


class DictionaryUpdateRequest(BaseModel):
    name: str
    description: Optional[str]
    category: str


# Простая проверка админского токена
def verify_admin_token(token: str) -> bool:
    """Проверяет валидность админского токена"""
    return token == "admin_token_" + settings.ADMIN_PASSWORD


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Вход в админку по паролю"""
    if request.password == settings.ADMIN_PASSWORD:
        token = "admin_token_" + settings.ADMIN_PASSWORD
        return AdminLoginResponse(success=True, token=token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )


@router.get("/dictionaries", response_model=list[DictionaryListResponse])
async def get_dictionaries():
    """Получить список всех словарей с количеством слов"""
    async with async_session_factory() as session:
        # Получаем все словари
        result = await session.execute(
            select(Dictionary).order_by(Dictionary.id)
        )
        dictionaries = result.scalars().all()
        
        # Для каждого словаря считаем количество слов
        response = []
        for dict_item in dictionaries:
            count_result = await session.execute(
                select(DictionaryWord).where(
                    DictionaryWord.dictionary_id == dict_item.id
                )
            )
            words_count = len(count_result.scalars().all())
            
            response.append(DictionaryListResponse(
                id=dict_item.id,
                name=dict_item.name,
                description=dict_item.description,
                category=dict_item.category,
                words_count=words_count
            ))
        
        return response


@router.get("/dictionaries/{dictionary_id}", response_model=DictionaryDetailResponse)
async def get_dictionary(dictionary_id: int):
    """Получить информацию о словаре"""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Dictionary).where(Dictionary.id == dictionary_id)
        )
        dictionary = result.scalar_one_or_none()
        
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Словарь не найден"
            )
        
        return DictionaryDetailResponse(
            id=dictionary.id,
            name=dictionary.name,
            description=dictionary.description,
            category=dictionary.category
        )


@router.get("/dictionaries/{dictionary_id}/words", response_model=list[WordInDictionaryResponse])
async def get_dictionary_words(dictionary_id: int):
    """Получить все слова в словаре"""
    async with async_session_factory() as session:
        # Проверяем существование словаря
        dict_result = await session.execute(
            select(Dictionary).where(Dictionary.id == dictionary_id)
        )
        if not dict_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Словарь не найден"
            )
        
        # Получаем все слова из словаря
        result = await session.execute(
            select(Word)
            .join(DictionaryWord, DictionaryWord.word_id == Word.id)
            .where(DictionaryWord.dictionary_id == dictionary_id)
            .order_by(Word.lemma)
        )
        words = result.scalars().all()
        
        return [
            WordInDictionaryResponse(
                id=word.id,
                lemma=word.lemma,
                pos=word.pos,
                level=word.level,
                translations=word.translations
            )
            for word in words
        ]


@router.delete("/dictionaries/{dictionary_id}")
async def delete_dictionary(dictionary_id: int):
    """Удалить словарь и все связи с словами"""
    async with async_session_factory() as session:
        # Проверяем существование словаря
        result = await session.execute(
            select(Dictionary).where(Dictionary.id == dictionary_id)
        )
        dictionary = result.scalar_one_or_none()
        
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Словарь не найден"
            )
        
        # Удаляем все связи с словами
        await session.execute(
            delete(DictionaryWord).where(
                DictionaryWord.dictionary_id == dictionary_id
            )
        )
        
        # Удаляем словарь
        await session.execute(
            delete(Dictionary).where(Dictionary.id == dictionary_id)
        )
        
        await session.commit()
        
        return {"success": True, "message": "Словарь удален"}


@router.put("/dictionaries/{dictionary_id}", response_model=DictionaryDetailResponse)
async def update_dictionary(dictionary_id: int, request: DictionaryUpdateRequest):
    """Обновить информацию о словаре"""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Dictionary).where(Dictionary.id == dictionary_id)
        )
        dictionary = result.scalar_one_or_none()
        
        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Словарь не найден"
            )
        
        # Обновляем поля
        dictionary.name = request.name
        dictionary.description = request.description
        dictionary.category = request.category
        
        await session.commit()
        await session.refresh(dictionary)
        
        return DictionaryDetailResponse(
            id=dictionary.id,
            name=dictionary.name,
            description=dictionary.description,
            category=dictionary.category
        )
