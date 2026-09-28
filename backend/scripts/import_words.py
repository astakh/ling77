"""
Import words from words.json file into dictionaries.
Usage: python scripts/import_words.py [--dictionary-id ID] [--dictionary-name NAME] [--dry-run]

Examples:
    # Import into existing dictionary
    python scripts/import_words.py --dictionary-id 1
    
    # Create new dictionary and import
    python scripts/import_words.py --dictionary-name "Новый словарь B1"
    
    # Dry run (show what would be imported without saving)
    python scripts/import_words.py --dictionary-id 1 --dry-run
"""

import asyncio
import json
import unicodedata
import sys
import os
import argparse
from typing import Optional

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from database import async_session_factory
from models import Dictionary, Word


def make_lemma_key(lemma: str) -> str:
    """Create normalized lemma key for duplicate detection."""
    return unicodedata.normalize("NFC", lemma).casefold().strip()


def load_words_file(filepath: str = "words.json") -> list[dict]:
    """Load words from JSON file."""
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found")
        print("\nExpected format:")
        print("""
[
  {
    "lemma": "house",
    "pos": "noun",
    "level": "A1",
    "translations": ["дом", "жилище"]
  },
  {
    "lemma": "run",
    "pos": "verb",
    "level": "A1",
    "translations": ["бежать", "бегать"]
  }
]
        """)
        sys.exit(1)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            words = json.load(f)
        
        if not isinstance(words, list):
            raise ValueError("JSON must be an array of word objects")
        
        # Validate structure
        for i, word in enumerate(words):
            if not isinstance(word, dict):
                raise ValueError(f"Item {i} is not an object")
            
            required_fields = ['lemma', 'pos', 'level', 'translations']
            for field in required_fields:
                if field not in word:
                    raise ValueError(f"Item {i} missing required field: {field}")
            
            if not isinstance(word['translations'], list):
                raise ValueError(f"Item {i}: 'translations' must be an array")
            
            if word['level'] not in ['A1', 'A2', 'B1', 'B2']:
                raise ValueError(f"Item {i}: invalid level '{word['level']}'. Must be A1, A2, B1, or B2")
        
        return words
    
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{filepath}'")
        print(f"   {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: Invalid data structure")
        print(f"   {e}")
        sys.exit(1)


async def import_words(
    words: list[dict],
    dictionary_id: Optional[int] = None,
    dictionary_name: Optional[str] = None,
    dry_run: bool = False
):
    """Import words into database."""
    
    async with async_session_factory() as session:
        # Get or create dictionary
        if dictionary_id:
            result = await session.execute(
                select(Dictionary).where(Dictionary.id == dictionary_id)
            )
            dictionary = result.scalar_one_or_none()
            
            if not dictionary:
                print(f"❌ Error: Dictionary with id={dictionary_id} not found")
                print("\nAvailable dictionaries:")
                result = await session.execute(select(Dictionary))
                dicts = result.scalars().all()
                for d in dicts:
                    print(f"  ID {d.id}: {d.name}")
                sys.exit(1)
        
        elif dictionary_name:
            # Check if dictionary exists
            result = await session.execute(
                select(Dictionary).where(Dictionary.name == dictionary_name)
            )
            dictionary = result.scalar_one_or_none()
            
            if not dictionary:
                if dry_run:
                    print(f"📝 Would create dictionary: '{dictionary_name}'")
                    dictionary = Dictionary(id=999, name=dictionary_name)  # Fake for dry run
                else:
                    dictionary = Dictionary(name=dictionary_name)
                    session.add(dictionary)
                    await session.flush()
                    print(f"✅ Created dictionary: '{dictionary.name}' (id={dictionary.id})")
        else:
            print("❌ Error: Must specify either --dictionary-id or --dictionary-name")
            sys.exit(1)
        
        # Import words
        created_count = 0
        skipped_count = 0
        errors = []
        
        print(f"\n📥 Importing {len(words)} words into dictionary '{dictionary.name}'...")
        if dry_run:
            print("🔍 DRY RUN MODE - no changes will be saved\n")
        
        for i, word_data in enumerate(words):
            try:
                lemma = word_data['lemma'].strip()
                pos = word_data['pos'].strip()
                level = word_data['level'].strip()
                translations = word_data['translations']
                
                if not lemma or not pos or not level:
                    errors.append(f"Item {i}: missing required fields")
                    continue
                
                # Create lemma key
                lemma_key = make_lemma_key(lemma)
                
                # Check for duplicates
                result = await session.execute(
                    select(Word).where(
                        Word.lemma_key == lemma_key,
                        Word.pos == pos,
                        Word.dictionary_id == dictionary.id,
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    skipped_count += 1
                    if not dry_run:
                        print(f"  ⏭️  Skipped: {lemma} ({pos}) - already exists")
                    continue
                
                # Add new word
                if not dry_run:
                    word = Word(
                        lemma=lemma,
                        lemma_key=lemma_key,
                        pos=pos,
                        level=level,
                        translations=translations,
                        dictionary_id=dictionary.id,
                    )
                    session.add(word)
                
                created_count += 1
                if not dry_run:
                    print(f"  ✅ Added: {lemma} ({pos}) - {', '.join(translations)}")
            
            except Exception as e:
                errors.append(f"Item {i} ({word_data.get('lemma', 'unknown')}): {str(e)}")
        
        # Commit if not dry run
        if not dry_run and created_count > 0:
            await session.commit()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Import Summary")
        print("=" * 50)
        print(f"  Total words in file: {len(words)}")
        print(f"  ✅ Created: {created_count}")
        print(f"  ⏭️  Skipped (duplicates): {skipped_count}")
        print(f"  ❌ Errors: {len(errors)}")
        
        if errors:
            print("\n❌ Errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        if dry_run:
            print("\n🔍 This was a dry run. No changes were saved.")
            print("   Remove --dry-run flag to actually import words.")
        
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Import words from words.json into dictionaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import into existing dictionary
  python scripts/import_words.py --dictionary-id 1
  
  # Create new dictionary and import
  python scripts/import_words.py --dictionary-name "Новый словарь B1"
  
  # Dry run (preview without saving)
  python scripts/import_words.py --dictionary-id 1 --dry-run
        """
    )
    
    parser.add_argument(
        '--dictionary-id',
        type=int,
        help='ID of existing dictionary to import into'
    )
    
    parser.add_argument(
        '--dictionary-name',
        type=str,
        help='Name of dictionary (will be created if doesn\'t exist)'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        default='words.json',
        help='Path to words.json file (default: words.json)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be imported without saving'
    )
    
    args = parser.parse_args()
    
    if not args.dictionary_id and not args.dictionary_name:
        parser.error("Must specify either --dictionary-id or --dictionary-name")
    
    # Load words
    print(f"📖 Loading words from '{args.file}'...")
    words = load_words_file(args.file)
    print(f"✅ Loaded {len(words)} words\n")
    
    # Import
    asyncio.run(import_words(
        words=words,
        dictionary_id=args.dictionary_id,
        dictionary_name=args.dictionary_name,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
