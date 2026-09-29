import { create } from 'zustand';
import { User, LearningProfile, Lesson, Exercise, ExerciseWord, DashboardSummary, Level, WordStatus } from '../types';
import { api } from '../api/client';

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

  // Declined words
  declinedWords: string[];

  // Loading
  isLoading: boolean;
  error: string | null;

  // Actions
  initialize: () => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  completeOnboarding: (timezone: string, level: Level, dictionaryId?: number | null) => Promise<void>;
  getDashboardSummary: () => Promise<DashboardSummary>;
  startLesson: () => Promise<Lesson>;
  loadCurrentLesson: () => Promise<Lesson | null>;
  previewLesson: () => Promise<{ words: { id: string; lemma: string; translations: string[]; isNew: boolean; isDue: boolean }[] }>;
  declineWord: (wordId: string) => void;
  submitExerciseTranslation: (translation: string) => void;
  evaluateExercise: (exerciseId: number, translation: string) => Promise<{ result: string; words: any[]; isLast: boolean; referenceTranslation: string; newSuggestedWords: Array<{ word: string; translation: string }> }>;
  nextExercise: () => void;
  completeLesson: () => Promise<void>;
  clearCurrentLesson: () => void;
  abandonLesson: () => Promise<void>;
  setExerciseDraft: (draft: string) => void;
  updateWordStatus: (userWordId: number, status: WordStatus) => Promise<void>;
  setDeclinedWords: (words: string[]) => void;
  clearError: () => void;
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
  isLoading: false,
  error: null,

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false });
      return;
    }

    try {
      // Get current user info
      const user = await api.auth.me();
      set({ 
        isAuthenticated: true,
        user: {
          id: String(user.id),
          email: user.email,
          timezone: user.timezone,
          isOnboarded: user.is_onboarded,
        }
      });
    } catch (error: any) {
      if (error.status === 401) {
        localStorage.removeItem('access_token');
        set({ isAuthenticated: false });
      }
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.auth.register(email, password);
      localStorage.setItem('access_token', response.access_token);
      
      // Load user info immediately after registration
      const userInfo = await api.auth.me();
      
      set({ 
        isAuthenticated: true,
        isLoading: false,
        user: {
          id: String(userInfo.id),
          email: userInfo.email,
          timezone: userInfo.timezone,
          isOnboarded: userInfo.is_onboarded,
        }
      });
    } catch (error: any) {
      set({ error: error.detail || 'Registration failed', isLoading: false });
      throw error;
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.auth.login(email, password);
      localStorage.setItem('access_token', response.access_token);
      
      // Load user info immediately after login
      const userInfo = await api.auth.me();
      
      set({ 
        isAuthenticated: true,
        isLoading: false,
        user: {
          id: String(userInfo.id),
          email: userInfo.email,
          timezone: userInfo.timezone,
          isOnboarded: userInfo.is_onboarded,
        }
      });
      return true;
    } catch (error: any) {
      set({ error: error.detail || 'Login failed', isLoading: false });
      return false;
    }
  },

  logout: async () => {
    try {
      await api.auth.logout();
    } catch (e) {
      // Ignore logout errors
    }
    localStorage.removeItem('access_token');
    set({
      isAuthenticated: false,
      user: null,
      profile: null,
      lessons: [],
      currentLesson: null,
      currentExerciseIndex: 0,
      streak: { count: 0, lastDate: '' },
      declinedWords: [],
    });
  },

  completeOnboarding: async (timezone: string, level: Level, dictionaryId?: number | null) => {
    set({ isLoading: true, error: null });
    try {
      await api.onboarding.complete(timezone, level);
      
      // If dictionary selected, set it as current
      if (dictionaryId) {
        try {
          await api.dictionaries.change(dictionaryId);
        } catch (err) {
          console.error('Failed to set dictionary:', err);
          // Don't fail onboarding if dictionary selection fails
        }
      }
      
      // Update user state
      set({ 
        isLoading: false,
        user: {
          ...get().user!,
          isOnboarded: true,
        }
      });
    } catch (error: any) {
      set({ error: error.detail || 'Onboarding failed', isLoading: false });
      throw error;
    }
  },

  getDashboardSummary: async () => {
    try {
      const summary = await api.dashboard.summary();
      const result: DashboardSummary = {
        cta: summary.cta,
        streak: summary.streak,
        totalLessons: summary.total_lessons,
        totalWords: summary.total_words,
        masteredWords: summary.mastered_words,
        dueWords: summary.due_words,
        lessonsToday: summary.lessons_today,
        currentLessonId: summary.current_lesson_id ? String(summary.current_lesson_id) : null,
      };
      return result;
    } catch (error: any) {
      set({ error: error.detail || 'Failed to load dashboard' });
      throw error;
    }
  },

  previewLesson: async () => {
    set({ isLoading: true, error: null });
    try {
      // Передаем declined words в backend чтобы получить замены
      const declinedIds = get().declinedWords.map(id => parseInt(id));
      const response = await api.lesson.preview(declinedIds);
      set({ isLoading: false });
      
      const words = response.words.map(w => ({
        id: String(w.id),
        lemma: w.lemma,
        translations: w.translations,
        isNew: w.is_new,
        isDue: w.is_due,
      }));
      
      return { words };
    } catch (error: any) {
      set({ error: error.detail || 'Failed to preview lesson', isLoading: false });
      throw error;
    }
  },

  declineWord: (wordId: string) => {
    const { declinedWords } = get();
    set({ declinedWords: [...declinedWords, wordId] });
  },

  setDeclinedWords: (words: string[]) => {
    set({ declinedWords: words });
  },

  startLesson: async () => {
    set({ isLoading: true, error: null });
    try {
      // Передаем declined words в backend
      const declinedIds = get().declinedWords.map(id => parseInt(id));
      const response = await api.lesson.start(declinedIds);
      
      // Convert API response to Lesson type
      const lesson: Lesson = {
        id: String(response.lesson_id),
        lessonNumber: response.lesson_number,
        status: 'in_progress',
        startedLocalDate: new Date().toISOString().split('T')[0],
        completedLocalDate: null,
        exercises: response.exercises.map((ex: any) => ({
          id: String(ex.id),
          orderIndex: ex.order_index,
          targetSentence: ex.target_sentence,
          referenceTranslation: ex.reference_translation,
          userTranslation: '',
          status: ex.status,
          words: ex.words.map((w: any) => ({
            wordId: String(w.word_id),
            isTarget: w.is_target,
            isNew: w.is_new,
            surfaceForm: w.surface_form,
            result: 'pending',
            userFragment: '',
            stageBefore: w.stage_before,
            stageAfter: w.stage_after,
          })),
        })),
      };

      set({
        currentLesson: lesson,
        currentExerciseIndex: 0,
        declinedWords: [],
        exerciseDraft: '',
        isLoading: false,
      });

      return lesson;
    } catch (error: any) {
      set({ error: error.detail || 'Failed to start lesson', isLoading: false });
      throw error;
    }
  },

  loadCurrentLesson: async () => {
    console.log('📥 Loading current lesson from backend...');
    set({ isLoading: true, error: null });
    try {
      const response = await api.lesson.getCurrent();
      
      if (!response.lesson) {
        console.log('   No current lesson found');
        set({ isLoading: false });
        return null;
      }
      
      console.log(`   Found lesson #${response.lesson.lesson_number} with ${response.lesson.exercises.length} exercises`);
      
      // Convert API response to Lesson type
      const lesson: Lesson = {
        id: String(response.lesson.id),
        lessonNumber: response.lesson.lesson_number,
        status: response.lesson.status as any,
        startedLocalDate: response.lesson.started_local_date,
        completedLocalDate: response.lesson.completed_local_date,
        exercises: response.lesson.exercises.map((ex: any) => ({
          id: String(ex.id),
          orderIndex: ex.order_index,
          targetSentence: ex.target_sentence,
          referenceTranslation: ex.reference_translation,
          userTranslation: ex.user_translation || '',
          status: ex.status,
          words: ex.words.map((w: any) => ({
            wordId: String(w.word_id),
            isTarget: w.is_target,
            isNew: w.is_new,
            surfaceForm: w.surface_form,
            result: w.result || 'pending',
            userFragment: w.user_fragment || '',
            stageBefore: w.stage_before,
            stageAfter: w.stage_after,
          })),
        })),
      };

      // Find first pending exercise
      const firstPendingIndex = lesson.exercises.findIndex(ex => ex.status === 'pending');
      const exerciseIndex = firstPendingIndex >= 0 ? firstPendingIndex : 0;
      
      console.log(`   Resuming from exercise ${exerciseIndex + 1}`);

      set({
        currentLesson: lesson,
        currentExerciseIndex: exerciseIndex,
        isLoading: false,
      });

      return lesson;
    } catch (error: any) {
      console.error('   Failed to load current lesson:', error);
      set({ error: error.detail || 'Failed to load current lesson', isLoading: false });
      return null;
    }
  },

  submitExerciseTranslation: (translation: string) => {
    set({ exerciseDraft: translation });
  },

  evaluateExercise: async (exerciseId: number, translation: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.lesson.evaluate(exerciseId, translation);
      set({ isLoading: false });
      return {
        result: response.result,
        words: response.words,
        isLast: response.is_last,
        referenceTranslation: response.reference_translation,
        newSuggestedWords: response.new_suggested_words || [],
      };
    } catch (error: any) {
      set({ error: error.detail || 'Failed to evaluate exercise', isLoading: false });
      throw error;
    }
  },

  nextExercise: () => {
    const { currentLesson, currentExerciseIndex } = get();
    if (!currentLesson) return;

    if (currentExerciseIndex < currentLesson.exercises.length - 1) {
      set({ currentExerciseIndex: currentExerciseIndex + 1, exerciseDraft: '' });
    }
  },

  completeLesson: async () => {
    // Lesson is auto-completed by backend when last exercise is evaluated
    // Don't clear currentLesson here - it's needed for the summary page
    // The summary page will handle cleanup
    set({ currentExerciseIndex: 0 });
  },

  clearCurrentLesson: () => {
    set({ currentLesson: null, currentExerciseIndex: 0 });
  },

  abandonLesson: async () => {
    const { currentLesson } = get();
    if (!currentLesson) return;

    set({ isLoading: true, error: null });
    try {
      await api.lesson.abandon(parseInt(currentLesson.id));
      set({
        currentLesson: null,
        currentExerciseIndex: 0,
        isLoading: false,
      });
    } catch (error: any) {
      set({ error: error.detail || 'Failed to abandon lesson', isLoading: false });
      throw error;
    }
  },

  setExerciseDraft: (draft: string) => {
    set({ exerciseDraft: draft });
  },

  updateWordStatus: async (userWordId: number, status: WordStatus) => {
    set({ isLoading: true, error: null });
    try {
      await api.vocabulary.updateStatus(userWordId, status);
      set({ isLoading: false });
    } catch (error: any) {
      set({ error: error.detail || 'Failed to update word status', isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
