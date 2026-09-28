// SRS intervals measured in lessons (not days)
export const SRS_INTERVALS = [1, 2, 3, 7, 11, 30];
export const MAX_STAGE = 6;

export function calculateNewStage(currentStage: number, result: 'correct' | 'typo' | 'incorrect' | 'dont_know'): number {
  if (result === 'correct' || result === 'typo') {
    return Math.min(currentStage + 1, MAX_STAGE);
  }
  // incorrect or dont_know
  return Math.max(currentStage - 1, 0);
}

export function calculateDueLessonNumber(currentLessonNumber: number, newStage: number): number | null {
  if (newStage >= MAX_STAGE) {
    return null; // mastered
  }
  const interval = SRS_INTERVALS[newStage];
  return currentLessonNumber + interval;
}

export function isDue(userWordStage: number, userWordDueLesson: number | null, currentLessonNumber: number): boolean {
  if (userWordDueLesson === null) return false; // mastered
  return userWordDueLesson <= currentLessonNumber;
}

export function isMastered(stage: number): boolean {
  return stage >= MAX_STAGE;
}
