/**
 * API client for WordFlow backend.
 * Handles JWT refresh, error handling, and request/response types.
 */

const API_BASE_URL = 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
}

async function refreshToken(): Promise<string> {
  console.log('🔄 Attempting to refresh token...');
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    credentials: 'include', // Важно: передаём cookies с refresh token
  });

  console.log(`🔄 Refresh response: ${response.status}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Refresh failed' }));
    console.error('❌ Refresh failed:', errorData);
    throw new ApiError(response.status, errorData.detail || 'Refresh failed');
  }

  const data = await response.json();
  console.log('✅ Token refreshed successfully');
  return data.access_token;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`);
  const token = localStorage.getItem('access_token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  let response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Важно: передаём cookies
  });

  console.log(`📥 API Response: ${response.status} ${response.statusText} from ${url}`);

  // Handle 401 — try refresh
  if (response.status === 401 && token) {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const newToken = await refreshToken();
        localStorage.setItem('access_token', newToken);
        isRefreshing = false;
        onRefreshed(newToken);

        // Retry original request
        (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
        response = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });
      } catch {
        isRefreshing = false;
        localStorage.removeItem('access_token');
        window.location.hash = '#/auth';
        throw new ApiError(401, 'Session expired');
      }
    } else {
      // Wait for refresh to complete
      return new Promise<T>((resolve) => {
        refreshSubscribers.push((newToken: string) => {
          (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
          fetch(url, { ...options, headers, credentials: 'include' })
            .then(r => r.json())
            .then(resolve);
        });
      });
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, errorData.detail || 'Request failed');
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// ============ API Methods ============

export const api = {
  // Auth
  auth: {
    register: (email: string, password: string) =>
      request<{ access_token: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    login: (email: string, password: string) =>
      request<{ access_token: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    logout: () =>
      request<{ status: string }>('/auth/logout', { method: 'POST', credentials: 'omit' }),

    me: () =>
      request<{
        id: number;
        email: string;
        timezone: string;
        is_onboarded: boolean;
        is_admin: boolean;
      }>('/auth/me'),
  },

  // Onboarding
  onboarding: {
    complete: (timezone: string, level: string) =>
      request<{ status: string }>('/onboarding/complete', {
        method: 'POST',
        body: JSON.stringify({ timezone, level }),
      }),
  },

  // Dashboard
  dashboard: {
    summary: () =>
      request<{
        cta: 'start' | 'resume' | 'limit_reached';
        streak: number;
        total_lessons: number;
        total_words: number;
        mastered_words: number;
        due_words: number;
        lessons_today: number;
        current_lesson_id: number | null;
      }>('/dashboard/summary'),
  },

  // Lesson
  lesson: {
    preview: (declinedWordIds: number[] = []) =>
      request<{
        words: { id: number; lemma: string; translations: string[]; is_new: boolean; is_due: boolean }[];
      }>('/lesson/preview', {
        method: 'POST',
        body: JSON.stringify({ declined_word_ids: declinedWordIds }),
      }),

    declineWord: (wordId: number) =>
      request<{ status: string }>('/lesson/new-word/decline', {
        method: 'POST',
        body: JSON.stringify({ word_id: wordId }),
      }),

    start: (declinedWordIds: number[] = [], idempotencyKey?: string) =>
      request<{
        lesson_id: number;
        lesson_number: number;
        exercises: any[];
      }>('/lesson/start', {
        method: 'POST',
        body: JSON.stringify({ declined_word_ids: declinedWordIds }),
        headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined,
      }),

    getCurrent: () =>
      request<{
        lesson: {
          id: number;
          lesson_number: number;
          status: string;
          started_local_date: string;
          completed_local_date: string | null;
          exercises: any[];
        } | null;
      }>('/lesson/current'),

    evaluate: (exerciseId: number, userTranslation: string, idempotencyKey?: string) =>
      request<{
        exercise_id: number;
        result: 'correct' | 'typo' | 'incorrect';
        words: any[];
        user_translation: string;
        reference_translation: string;
        is_last: boolean;
        new_suggested_words: Array<{ word: string; translation: string }>;
      }>('/lesson/evaluate', {
        method: 'POST',
        body: JSON.stringify({ exercise_id: exerciseId, user_translation: userTranslation }),
        headers: idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined,
      }),

    summary: (lessonId: number) =>
      request<any>(`/lesson/${lessonId}/summary`),

    abandon: (lessonId: number) =>
      request<{ status: string }>(`/lesson/${lessonId}/abandon`, { method: 'POST' }),
  },

  // Vocabulary
  vocabulary: {
    list: (page = 1, pageSize = 20, status?: string, search?: string) => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (status) params.set('status', status);
      if (search) params.set('search', search);
      return request<any>(`/vocabulary/list?${params}`);
    },

    updateStatus: (userWordId: number, status: string) =>
      request<{ status: string }>(`/vocabulary/word/${userWordId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
  },

  // Dictionaries
  dictionaries: {
    list: (category?: string, search?: string) => {
      const params = new URLSearchParams();
      if (category) params.set('category', category);
      if (search) params.set('search', search);
      const query = params.toString();
      return request<{ dictionaries: any[] }>(`/dictionaries${query ? `?${query}` : ''}`);
    },

    get: (id: number) =>
      request<any>(`/dictionaries/${id}`),

    getProfile: () =>
      request<{
        user_id: number;
        level: string;
        dictionary_id: number | null;
        daily_lesson_limit: number;
        words_per_lesson: number;
        last_lesson_number: number;
      }>('/dictionaries/profile'),

    getCurrent: () =>
      request<{ dictionary: any | null; message?: string }>('/dictionaries/profile/current'),

    change: (dictionaryId: number) =>
      request<{ status: string; dictionary_id: number; dictionary_name: string }>(
        '/dictionaries/profile/dictionary',
        {
          method: 'PATCH',
          body: JSON.stringify({ dictionary_id: dictionaryId }),
        }
      ),
  },

  // Settings
  settings: {
    update: (settings: {
      level: string;
      words_per_lesson: number;
      lessons_per_day: number;
      dictionary_id: number;
    }) =>
      request<{ status: string }>('/settings', {
        method: 'PATCH',
        body: JSON.stringify(settings),
      }),
  },
};

export { ApiError };
