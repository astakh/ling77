import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { Flame, BookOpen, Brain, Target, Play, Clock, LogOut, List, Library, Settings } from 'lucide-react';
import { DashboardSummary } from '../types';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { logout, profile } = useStore();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🏠 DashboardPage: Component mounted');
    console.log('🏠 DashboardPage: Current profile:', useStore.getState().profile);
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    console.log('🏠 DashboardPage: Loading dashboard data');
    try {
      const data = await useStore.getState().getDashboardSummary();
      console.log('🏠 DashboardPage: Dashboard data loaded:', data);
      setSummary(data);
    } catch (error) {
      console.error('❌ DashboardPage: Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCTA = () => {
    console.log('🎯 Dashboard CTA clicked');
    console.log('   summary:', summary);
    
    if (!summary) return;
    
    if (summary.cta === 'resume' && summary.currentLessonId) {
      console.log(`   Resuming lesson #${summary.currentLessonId}`);
      navigate('/lesson/exercise');
    } else if (summary.cta === 'start') {
      console.log('   Starting new lesson');
      navigate('/lesson/preview');
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-red-500">Ошибка загрузки</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">WordFlow</h1>
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
        <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-5 text-white shadow-lg animate-slide-up">
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
        <div className="grid grid-cols-2 gap-3 animate-fade-in">
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
              {summary.lessonsToday}/{profile?.dailyLessonLimit || 5}
            </div>
          </div>
        </div>

        {/* CTA */}
        {summary.cta === 'limit_reached' ? (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-center">
            <div className="text-4xl mb-2">🎉</div>
            <h3 className="font-semibold text-amber-800">Лимит на сегодня исчерпан</h3>
            <p className="text-sm text-amber-600 mt-1">Вы прошли {summary.lessonsToday} уроков. Возвращайтесь завтра!</p>
          </div>
        ) : (
          <button
            onClick={handleCTA}
            className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-2xl hover:bg-indigo-700 transition flex items-center justify-center gap-3 shadow-lg shadow-indigo-200 text-lg"
          >
            <Play className="w-6 h-6" />
            {summary.cta === 'resume' ? 'Продолжить урок' : 'Начать урок'}
          </button>
        )}
      </div>
    </div>
  );
}
