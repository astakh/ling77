import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { Level } from '../types';
import { GraduationCap, Globe, ArrowRight, BookOpen } from 'lucide-react';
import { api } from '../api/client';

const LEVELS: { value: Level; label: string; description: string }[] = [
  { value: 'A1', label: 'A1 — Начальный', description: 'Базовые слова и фразы' },
  { value: 'A2', label: 'A2 — Элементарный', description: 'Простые повседневные темы' },
  { value: 'B1', label: 'B1 — Средний', description: 'Свободное общение на знакомые темы' },
  { value: 'B2', label: 'B2 — Выше среднего', description: 'Сложные тексты и абстрактные темы' },
];

interface Dictionary {
  id: number;
  name: string;
  description: string | null;
  category: string;
  total_words: number;
}

const CATEGORY_LABELS: Record<string, string> = {
  general: '📚 Общий',
  it: '💻 IT',
  travel: '✈️ Путешествия',
  business: '💼 Бизнес',
  food: '🍽️ Еда',
  medical: '🏥 Медицина',
  daily: '💬 Повседневное',
};

export default function OnboardingPage() {
  const [level, setLevel] = useState<Level>('A1');
  const [timezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone || 'Europe/Moscow');
  const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
  const [selectedDictId, setSelectedDictId] = useState<number | null>(null);
  const { completeOnboarding, isLoading } = useStore();

  useEffect(() => {
    // Load dictionaries
    api.dictionaries.list().then(res => {
      setDictionaries(res.dictionaries);
      // Select "Общий словарь" by default
      const generalDict = res.dictionaries.find(d => d.category === 'general' && d.name.includes('Общий'));
      if (generalDict) {
        setSelectedDictId(generalDict.id);
      }
    }).catch(err => {
      console.error('Failed to load dictionaries:', err);
    });
  }, []);

  const handleComplete = async () => {
    try {
      await completeOnboarding(timezone, level, selectedDictId);
      // Redirect will be handled by App.tsx after user state is updated
    } catch (error: any) {
      console.error('Onboarding failed:', error);
      // If already onboarded, just redirect to dashboard
      if (error.detail === 'Already onboarded') {
        window.location.hash = '#/dashboard';
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl mb-4 shadow-lg">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Настройка обучения</h1>
          <p className="text-gray-500 mt-1">Выберите ваш уровень английского</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <div className="space-y-3 mb-6">
            {LEVELS.map(l => (
              <button
                key={l.value}
                onClick={() => setLevel(l.value)}
                className={`w-full p-4 rounded-xl border-2 text-left transition ${
                  level === l.value
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-100 hover:border-gray-200'
                }`}
              >
                <div className="font-semibold text-gray-800">{l.label}</div>
                <div className="text-sm text-gray-500 mt-0.5">{l.description}</div>
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-500 mb-6 bg-gray-50 p-3 rounded-lg">
            <Globe className="w-4 h-4" />
            <span>Часовой пояс: {timezone}</span>
          </div>

          {/* Dictionary selection */}
          {dictionaries.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <BookOpen className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Выберите словарь</span>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {dictionaries.map(dict => (
                  <button
                    key={dict.id}
                    onClick={() => setSelectedDictId(dict.id)}
                    className={`w-full p-3 rounded-lg border-2 text-left transition ${
                      selectedDictId === dict.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-100 hover:border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-800 text-sm">
                          {CATEGORY_LABELS[dict.category] || dict.category} {dict.name}
                        </div>
                        {dict.description && (
                          <div className="text-xs text-gray-500 mt-0.5">{dict.description}</div>
                        )}
                      </div>
                      <div className="text-xs text-gray-400">{dict.total_words} слов</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleComplete}
            disabled={isLoading || !selectedDictId}
            className="w-full py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Загрузка...
              </>
            ) : (
              <>
                Начать обучение
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
