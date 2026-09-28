import { create } from 'zustand';
import { User, LearningProfile, Lesson, Exercise, ExerciseWord, DashboardSummary, Level, WordStatus } from '../types';
import { dictionary, getWordById } from '../data/words';
import { getSentenceForWord } from '../data/sentences';
import { calculateNewStage, calculateDueLessonNumber, isDue, isMastered } from '../utils/srs';
import {
  saveUser, loadUser, saveProfile, loadProfile,
  saveLessons, loadLessons, saveStreak, loadStreak,
  saveAuth, loadAuth, clearAll, getLocalDate, getLessonsToday
} from '../utils/storage';

interface AppState {
  // Auth
  isAuthenticated: boolean;
  user: User | null;
  profile: LearningProfile | null;
  lessons: Lesson[];

  // Current lesson
  currentLesson: Lesson | null;
  currentExerciseIndex: number;

  // Streak
  streak: { count: number; lastDate: string };

  // Draft
  exerciseDraft: string;

  // Actions
  initialize: () => void;
  register: (email: string, password: string) => void;
  login: (email: string, password: string) => boolean;
  logout: () => void;
  completeOnboarding: (timezone: string, level: Level) => void;
  getDashboardSummary: () => DashboardSummary;
  startLesson: () => Lesson;
  previewLesson: () => { words: { id: string; lemma: string; translations: string[]; isNew: boolean; isDue: boolean }[] };
  declineWord: (wordId: string) => void;
  submitExerciseTranslation: (translation: string) => void;
  evaluateExercise: (result: 'correct' | 'typo' | 'incorrect' | 'dont_know') => void;
  nextExercise: () => void;
  completeLesson: () => void;
  abandonLesson: () => void;
  setExerciseDraft: (draft: string) => void;
  updateWordStatus: (userWordIndex: number, status: WordStatus) => void;
  getDeclinedWords: () => string[];
  setDeclinedWords: (words: string[]) => void;
  declinedWords: string[];
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
}

function deterministicShuffle<T>(items: T[], seed: string): T[] {
  const arr = [...items];
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i);
    hash |= 0;
  }
  for (let i = arr.length - 1; i > 0; i--) {
    hash = (hash * 1103515245 + 12345) & 0x7fffffff;
    const j = hash % (i + 1);
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export const useStore = create<AppState>((set, get) => ({
  isAuthenticated: false,
  user: null,
  profile: null,
  lessons: [],
  currentLesson: null,
  currentExerciseIndex: 0,
  streak: { count: 0, lastDate: '' },
  exerciseDraft: '',
  declinedWords: [],

  initialize: () => {
    const isAuth = loadAuth();
    const user = loadUser();
    const profile = loadProfile();
    const lessons = loadLessons();
    const streak = loadStreak();

    set({
      isAuthenticated: isAuth,
      user,
      profile,
      lessons,
      streak,
    });
  },

  register: (email: string, _password: string) => {
    const user: User = {
      id: generateId(),
      email: email.toLowerCase(),
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Europe/Moscow',
      isOnboarded: false,
    };
    saveUser(user);
    saveAuth(true);
    set({ isAuthenticated: true, user });
  },

  login: (email: string, _password: string) => {
    const user = loadUser();
    if (user && user.email === email.toLowerCase()) {
      saveAuth(true);
      const profile = loadProfile();
      const lessons = loadLessons();
      const streak = loadStreak();
      set({ isAuthenticated: true, user, profile, lessons, streak });
      return true;
    }
    return false;
  },

  logout: () => {
    clearAll();
    set({
      isAuthenticated: false,
      user: null,
      profile: null,
      lessons: [],
      currentLesson: null,
      currentExerciseIndex: 0,
      streak: { count: 0, lastDate: '' },
    });
  },

  completeOnboarding: (timezone: string, level: Level) => {
    const { user } = get();
    if (!user) return;

    const updatedUser: User = { ...user, timezone, isOnboarded: true };
    const profile: LearningProfile = {
      userId: user.id,
      level,
      dictionaryId: null,
      dailyLessonLimit: 5,
      lastLessonNumber: 0,
      userWords: [],
    };

    saveUser(updatedUser);
    saveProfile(profile);

    set({ user: updatedUser, profile });
  },

  getDashboardSummary: () => {
    const { profile, lessons, streak } = get();
    if (!profile) {
      return { cta: 'start' as const, streak: 0, totalLessons: 0, totalWords: 0, masteredWords: 0, dueWords: 0, lessonsToday: 0, currentLessonId: null };
    }

    const today = getLocalDate();
    const lessonsToday = getLessonsToday(lessons);
    const inProgress = lessons.find(l => l.status === 'in_progress');

    const totalWords = profile.userWords.length;
    const masteredWords = profile.userWords.filter(uw => isMastered(uw.stage)).length;
    const dueWords = profile.userWords.filter(uw => isDue(uw.stage, uw.dueLessonNumber, profile.lastLessonNumber)).length;

    let cta: 'start' | 'resume' | 'limit_reached';
    if (inProgress) {
      cta = 'resume';
    } else if (lessonsToday >= profile.dailyLessonLimit) {
      cta = 'limit_reached';
    } else {
      cta = 'start';
    }

    return {
      cta,
      streak: streak.count,
      totalLessons: lessons.filter(l => l.status === 'completed').length,
      totalWords,
      masteredWords,
      dueWords,
      lessonsToday,
      currentLessonId: inProgress?.id || null,
    };
  },

  previewLesson: () => {
    const { profile, declinedWords } = get();
    if (!profile) return { words: [] };

    const nextLessonNumber = profile.lastLessonNumber + 1;
    const seed = `${profile.userId}:${nextLessonNumber}`;

    // Get due words
    const dueWords = profile.userWords.filter(uw =>
      isDue(uw.stage, uw.dueLessonNumber, profile.lastLessonNumber) && !declinedWords.includes(uw.wordId)
    );

    // Get new words (not yet in userWords)
    const existingWordIds = new Set(profile.userWords.map(uw => uw.wordId));
    const availableNewWords = dictionary
      .filter(w => w.level === profile.level || (profile.level === 'A2' && w.level === 'A1') || (profile.level === 'B1' && (w.level === 'A1' || w.level === 'A2')) || (profile.level === 'B2' && (w.level === 'A1' || w.level === 'A2' || w.level === 'B1')))
      .filter(w => !existingWordIds.has(w.id))
      .filter(w => !declinedWords.includes(w.id));

    const shuffledDue = deterministicShuffle(dueWords, seed + ':due');
    const shuffledNew = deterministicShuffle(availableNewWords, seed + ':new');

    // Pick up to 5 due words and fill remaining with new words (up to 8 total)
    const selectedDue = shuffledDue.slice(0, 5);
    const remaining = 8 - selectedDue.length;
    const selectedNew = shuffledNew.slice(0, Math.max(remaining, 3));

    const words = [
      ...selectedDue.map(uw => {
        const word = getWordById(uw.wordId)!;
        return { id: word.id, lemma: word.lemma, translations: word.translations, isNew: false, isDue: true };
      }),
      ...selectedNew.map(w => ({ id: w.id, lemma: w.lemma, translations: w.translations, isNew: true, isDue: false })),
    ];

    return { words };
  },

  getDeclinedWords: () => get().declinedWords,
  setDeclinedWords: (words: string[]) => set({ declinedWords: words }),

  declineWord: (wordId: string) => {
    const { declinedWords } = get();
    set({ declinedWords: [...declinedWords, wordId] });
  },

  startLesson: () => {
    const { profile, lessons, declinedWords } = get();
    if (!profile) throw new Error('No profile');

    const nextLessonNumber = profile.lastLessonNumber + 1;
    const seed = `${profile.userId}:${nextLessonNumber}`;

    // Get due words
    const dueWords = profile.userWords.filter(uw =>
      isDue(uw.stage, uw.dueLessonNumber, profile.lastLessonNumber) && !declinedWords.includes(uw.wordId)
    );

    // Get new words
    const existingWordIds = new Set(profile.userWords.map(uw => uw.wordId));
    const availableNewWords = dictionary
      .filter(w => w.level === profile.level || (profile.level === 'A2' && w.level === 'A1') || (profile.level === 'B1' && (w.level === 'A1' || w.level === 'A2')) || (profile.level === 'B2' && (w.level === 'A1' || w.level === 'A2' || w.level === 'B1')))
      .filter(w => !existingWordIds.has(w.id))
      .filter(w => !declinedWords.includes(w.id));

    const shuffledDue = deterministicShuffle(dueWords, seed + ':due');
    const shuffledNew = deterministicShuffle(availableNewWords, seed + ':new');

    const selectedDue = shuffledDue.slice(0, 5);
    const remaining = 8 - selectedDue.length;
    const selectedNew = shuffledNew.slice(0, Math.max(remaining, 3));

    // Create exercises - group words into clusters of 2-3
    const allWords = [
      ...selectedDue.map(uw => ({ wordId: uw.wordId, isNew: false, stage: uw.stage })),
      ...selectedNew.map(w => ({ wordId: w.id, isNew: true, stage: 0 })),
    ];

    // Group into clusters of 2-3
    const clusters: typeof allWords[] = [];
    let i = 0;
    while (i < allWords.length) {
      const clusterSize = Math.min(2 + Math.floor(Math.random() * 2), allWords.length - i);
      clusters.push(allWords.slice(i, i + clusterSize));
      i += clusterSize;
    }

    const exercises: Exercise[] = clusters.map((cluster, idx) => {
      // Generate a sentence that uses the target words
      const targetWord = getWordById(cluster[0].wordId)!;
      const template = getSentenceForWord(targetWord);

      const exerciseWords: ExerciseWord[] = cluster.map(cw => {
        const word = getWordById(cw.wordId)!;
        return {
          wordId: cw.wordId,
          isTarget: true,
          isNew: cw.isNew,
          surfaceForm: word.lemma,
          result: 'pending' as const,
          userFragment: '',
          stageBefore: cw.stage,
          stageAfter: cw.stage,
        };
      });

      return {
        id: generateId(),
        orderIndex: idx,
        targetSentence: template.sentence,
        referenceTranslation: template.translation,
        userTranslation: '',
        status: 'pending' as const,
        words: exerciseWords,
      };
    });

    const lesson: Lesson = {
      id: generateId(),
      lessonNumber: nextLessonNumber,
      status: 'in_progress',
      startedLocalDate: getLocalDate(),
      completedLocalDate: null,
      exercises,
    };

    const updatedLessons = [...lessons, lesson];
    const updatedProfile: LearningProfile = {
      ...profile,
      lastLessonNumber: nextLessonNumber,
    };

    saveLessons(updatedLessons);
    saveProfile(updatedProfile);

    // Reset declined words
    set({
      lessons: updatedLessons,
      profile: updatedProfile,
      currentLesson: lesson,
      currentExerciseIndex: 0,
      declinedWords: [],
      exerciseDraft: '',
    });

    return lesson;
  },

  submitExerciseTranslation: (translation: string) => {
    const { currentLesson, currentExerciseIndex } = get();
    if (!currentLesson) return;

    const updatedExercises = [...currentLesson.exercises];
    updatedExercises[currentExerciseIndex] = {
      ...updatedExercises[currentExerciseIndex],
      userTranslation: translation,
    };

    set({
      currentLesson: { ...currentLesson, exercises: updatedExercises },
      exerciseDraft: translation,
    });
  },

  evaluateExercise: (result: 'correct' | 'typo' | 'incorrect' | 'dont_know') => {
    const { currentLesson, currentExerciseIndex, profile, lessons } = get();
    if (!currentLesson || !profile) return;

    const exercise = currentLesson.exercises[currentExerciseIndex];
    const updatedWords: ExerciseWord[] = exercise.words.map(ew => {
      if (!ew.isTarget) return ew;

      const newStage = result === 'dont_know'
        ? calculateNewStage(ew.stageBefore, 'incorrect')
        : calculateNewStage(ew.stageBefore, result);

      return {
        ...ew,
        result,
        stageAfter: newStage,
        userFragment: ew.surfaceForm,
      };
    });

    const updatedExercise: Exercise = {
      ...exercise,
      status: 'evaluated',
      words: updatedWords,
    };

    const updatedExercises = [...currentLesson.exercises];
    updatedExercises[currentExerciseIndex] = updatedExercise;

    const updatedLesson: Lesson = {
      ...currentLesson,
      exercises: updatedExercises,
    };

    // Update user words in profile
    const updatedUserWords = [...profile.userWords];
    updatedWords.forEach(ew => {
      if (!ew.isTarget) return;
      const existingIdx = updatedUserWords.findIndex(uw => uw.wordId === ew.wordId);
      const newDueLesson = calculateDueLessonNumber(currentLesson.lessonNumber, ew.stageAfter);

      if (existingIdx >= 0) {
        updatedUserWords[existingIdx] = {
          ...updatedUserWords[existingIdx],
          stage: ew.stageAfter,
          dueLessonNumber: newDueLesson,
          status: isMastered(ew.stageAfter) ? 'mastered' : 'active',
        };
      } else {
        updatedUserWords.push({
          wordId: ew.wordId,
          status: isMastered(ew.stageAfter) ? 'mastered' : 'active',
          stage: ew.stageAfter,
          dueLessonNumber: newDueLesson,
        });
      }
    });

    const updatedProfile: LearningProfile = { ...profile, userWords: updatedUserWords };
    const updatedLessons = lessons.map(l => l.id === updatedLesson.id ? updatedLesson : l);

    saveProfile(updatedProfile);
    saveLessons(updatedLessons);

    set({
      currentLesson: updatedLesson,
      profile: updatedProfile,
      lessons: updatedLessons,
    });
  },

  nextExercise: () => {
    const { currentLesson, currentExerciseIndex } = get();
    if (!currentLesson) return;

    if (currentExerciseIndex < currentLesson.exercises.length - 1) {
      set({ currentExerciseIndex: currentExerciseIndex + 1, exerciseDraft: '' });
    }
  },

  completeLesson: () => {
    const { currentLesson, lessons, streak } = get();
    if (!currentLesson) return;

    const today = getLocalDate();
    const completedLesson: Lesson = {
      ...currentLesson,
      status: 'completed',
      completedLocalDate: today,
    };

    const updatedLessons = lessons.map(l => l.id === completedLesson.id ? completedLesson : l);

    // Update streak
    let newStreak = { ...streak };
    if (streak.lastDate === today) {
      // Already counted today
    } else {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const yesterdayStr = yesterday.toISOString().split('T')[0];

      if (streak.lastDate === yesterdayStr) {
        newStreak = { count: streak.count + 1, lastDate: today };
      } else {
        newStreak = { count: 1, lastDate: today };
      }
    }

    saveLessons(updatedLessons);
    saveStreak(newStreak);

    set({
      lessons: updatedLessons,
      currentLesson: completedLesson,
      streak: newStreak,
    });
  },

  abandonLesson: () => {
    const { currentLesson, lessons } = get();
    if (!currentLesson) return;

    const abandonedLesson: Lesson = {
      ...currentLesson,
      status: 'abandoned',
    };

    const updatedLessons = lessons.map(l => l.id === abandonedLesson.id ? abandonedLesson : l);
    saveLessons(updatedLessons);

    set({
      lessons: updatedLessons,
      currentLesson: null,
      currentExerciseIndex: 0,
    });
  },

  setExerciseDraft: (draft: string) => {
    set({ exerciseDraft: draft });
    localStorage.setItem('lw_exercise_draft', draft);
  },

  updateWordStatus: (userWordIndex: number, status: WordStatus) => {
    const { profile } = get();
    if (!profile) return;

    const updatedUserWords = [...profile.userWords];
    updatedUserWords[userWordIndex] = { ...updatedUserWords[userWordIndex], status };

    const updatedProfile = { ...profile, userWords: updatedUserWords };
    saveProfile(updatedProfile);
    set({ profile: updatedProfile });
  },
}));
