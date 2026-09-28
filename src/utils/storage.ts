import { User, LearningProfile, Lesson } from '../types';

const STORAGE_KEYS = {
  USER: 'lw_user',
  PROFILE: 'lw_profile',
  LESSONS: 'lw_lessons',
  STREAK: 'lw_streak',
  AUTH: 'lw_auth',
};

export function saveUser(user: User): void {
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
}

export function loadUser(): User | null {
  const data = localStorage.getItem(STORAGE_KEYS.USER);
  return data ? JSON.parse(data) : null;
}

export function saveProfile(profile: LearningProfile): void {
  localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
}

export function loadProfile(): LearningProfile | null {
  const data = localStorage.getItem(STORAGE_KEYS.PROFILE);
  return data ? JSON.parse(data) : null;
}

export function saveLessons(lessons: Lesson[]): void {
  localStorage.setItem(STORAGE_KEYS.LESSONS, JSON.stringify(lessons));
}

export function loadLessons(): Lesson[] {
  const data = localStorage.getItem(STORAGE_KEYS.LESSONS);
  return data ? JSON.parse(data) : [];
}

export function saveStreak(streak: { count: number; lastDate: string }): void {
  localStorage.setItem(STORAGE_KEYS.STREAK, JSON.stringify(streak));
}

export function loadStreak(): { count: number; lastDate: string } {
  const data = localStorage.getItem(STORAGE_KEYS.STREAK);
  return data ? JSON.parse(data) : { count: 0, lastDate: '' };
}

export function saveAuth(isLoggedIn: boolean): void {
  localStorage.setItem(STORAGE_KEYS.AUTH, JSON.stringify(isLoggedIn));
}

export function loadAuth(): boolean {
  const data = localStorage.getItem(STORAGE_KEYS.AUTH);
  return data ? JSON.parse(data) : false;
}

export function clearAll(): void {
  Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
}

export function getLocalDate(): string {
  return new Date().toISOString().split('T')[0];
}

export function getLessonsToday(lessons: Lesson[]): number {
  const today = getLocalDate();
  return lessons.filter(l => l.startedLocalDate === today && l.status !== 'abandoned').length;
}
