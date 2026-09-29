"""SRS (Spaced Repetition System) logic — intervals in lessons, not days."""

# Stage intervals: after reaching stage N, the word is due again after INTERVALS[N] lessons
SRS_INTERVALS = [1, 2, 3, 7, 11, 30]
MAX_STAGE = 6


def calculate_new_stage(current_stage: int, result: str) -> int:
    """
    Calculate new SRS stage after evaluation.
    - correct/typo: stage + 1 (capped at MAX_STAGE)
    - incorrect/dont_know: max(stage - 1, 0)
    """
    if result in ("correct", "typo"):
        return min(current_stage + 1, MAX_STAGE)
    return max(current_stage - 1, 0)


def calculate_due_lesson_number(current_lesson_number: int, new_stage: int) -> int | None:
    """
    Calculate when the word is due next.
    Returns None if word is mastered (stage >= MAX_STAGE).
    """
    if new_stage >= MAX_STAGE:
        return None  # mastered
    interval = SRS_INTERVALS[new_stage]
    return current_lesson_number + interval


def is_due(stage: int, due_lesson_number: int | None, current_lesson_number: int) -> bool:
    """Check if a word is due for review at the given lesson number."""
    if due_lesson_number is None:
        return False  # mastered
    return due_lesson_number <= current_lesson_number


def is_mastered(stage: int) -> bool:
    return stage >= MAX_STAGE
