import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Globe, ArrowRight } from 'lucide-react';

type Level = 'A1' | 'A2' | 'B1' | 'B2';

const LEVELS: { value: Level; label: string; description: string }[] = [
  { value: 'A1', label: 'A1 — Начальный', description: 'Базовые слова и фразы' },
  { value: 'A2', label: 'A2 — Элементарный', description: 'Простые повседневные темы' },
  { value: 'B1', label: 'B1 — Средний', description: 'Свободное общение на знакомые темы' },
  { value: 'B2', label: 'B2 — Выше среднего', description: 'Сложные тексты и абстрактные темы' },
];

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [level, setLevel] = useState<Level>('A1');
  const [timezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone || 'Europe/Moscow');
  const [loading, setLoading] = useState(false);

  const handleComplete = async () => {
    setLoading(true);
    try {
      // TODO: Call API to complete onboarding
      setTimeout(() => {
        navigate('/dashboard');
      }, 500);
    } catch (error) {
      console.error('Onboarding failed:', error);
    } finally {
      setLoading(false);
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

          <button
            onClick={handleComplete}
            disabled={loading}
            className="w-full py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 disabled:opacity-50"
          >
            {loading ? (
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
