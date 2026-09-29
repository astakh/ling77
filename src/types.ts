export type Level = 'A1' | 'A2' | 'B1' | 'B2';

export type WordStatus = 'active' | 'mastered' | 'ignored';

export type LessonStatus = 'in_progress' | 'completed' | 'abandoned';

export type ExerciseStatus = 'pending' | 'evaluated';

export type ExerciseResult = 'correct' | 'typo' | 'incorrect' | 'dont_know' | 'pending';

export interface Word {
  id: string;
  lemma: string;
  pos: string; // part of speech
  level: Level;
  translations: string[];
}

export interface UserWord {
  wordId: string;
  status: WordStatus;
  stage: number; // 0-6
  dueLessonNumber: number | null;
}

export interface ExerciseWord {
  wordId: string;
  isTarget: boolean;
  isNew: boolean;
  surfaceForm: string;
  result: ExerciseResult;
  userFragment: string;
  stageBefore: number;
  stageAfter: number;
}

export interface Exercise {
  id: string;
  orderIndex: number;
  targetSentence: string;
  referenceTranslation: string;
  userTranslation: string;
  status: ExerciseStatus;
  words: ExerciseWord[];
}

export interface Lesson {
  id: string;
  lessonNumber: number;
  status: LessonStatus;
  startedLocalDate: string; // ISO date string
  completedLocalDate: string | null;
  exercises: Exercise[];
}

export interface LearningProfile {
  userId: string;
  level: Level;
  dictionaryId: number | null;
  dailyLessonLimit: number;
  wordsPerLesson: number;
  lastLessonNumber: number;
  userWords: UserWord[];
}

export interface User {
  id: string;
  email: string;
  timezone: string;
  isOnboarded: boolean;
}

export interface DashboardSummary {
  cta: 'start' | 'resume' | 'limit_reached';
  streak: number;
  totalLessons: number;
  totalWords: number;
  masteredWords: number;
  dueWords: number;
  lessonsToday: number;
  currentLessonId: string | null;
}
