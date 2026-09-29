import { useNavigate } from 'react-router-dom';
import { Flame, BookOpen, Brain, Target, Play, Clock, LogOut, List, Library, Settings } from 'lucide-react';

export default function DashboardPage() {
  const navigate = useNavigate();

  // TODO: Load actual data from API
  const summary = {
    cta: 'start' as const,
    streak: 0,
    totalLessons: 0,
    totalWords: 0,
    masteredWords: 0,
    dueWords: 0,
    lessonsToday: 0,
    currentLessonId: null,
  };

  const handleCTA = () => {
    if (summary.cta === 'start') {
      navigate('/lesson/preview');
    }
  };

  const handleLogout = () => {
    // TODO: Implement logout
    navigate('/auth');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Кругослов</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/dictionaries')}
              className="p-2 text-gray-500 hover:text-indigo-600 transition"
              title="Словари"
            >
              <Library className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/vocabulary')}
              className="p-2 text-gray-500 hover:text-indigo-600 transition"
              title="Мои слова"
            >
              <List className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/settings')}
              className="p-2 text-gray-500 hover:text-indigo-600 transition"
              title="Настройки"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-500 hover:text-red-500 transition"
              title="Выйти"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-lg mx-auto p-4 space-y-6">
        {/* Streak */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-5 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-3 rounded-xl">
              <Flame className="w-7 h-7" />
            </div>
            <div>
              <div className="text-3xl font-bold">{summary.streak}</div>
              <div className="text-sm text-white/80">дней подряд</div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-1">
              <BookOpen className="w-4 h-4 text-indigo-500" />
              <span className="text-xs text-gray-500">Уроков</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">{summary.totalLessons}</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-1">
              <Brain className="w-4 h-4 text-purple-500" />
              <span className="text-xs text-gray-500">Выучено</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">{summary.masteredWords}</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-1">
              <Target className="w-4 h-4 text-green-500" />
              <span className="text-xs text-gray-500">К повторению</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">{summary.dueWords}</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-amber-500" />
              <span className="text-xs text-gray-500">Сегодня</span>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {summary.lessonsToday}/5
            </div>
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={handleCTA}
          className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-2xl hover:bg-indigo-700 transition flex items-center justify-center gap-3 shadow-lg shadow-indigo-200 text-lg"
        >
          <Play className="w-6 h-6" />
          Начать урок
        </button>
      </div>
    </div>
  );
}
