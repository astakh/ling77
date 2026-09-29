import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { ArrowLeft, Save, User, BookOpen, Target, Calendar } from 'lucide-react';
import type { Level } from '../types';

interface Dictionary {
  id: number;
  name: string;
  description: string | null;
  category: string;
  total_words: number;
}

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, profile } = useStore();
  
  const [level, setLevel] = useState<Level>(profile?.level || 'A1');
  const [wordsPerLesson, setWordsPerLesson] = useState(profile?.wordsPerLesson || 8);
  const [lessonsPerDay, setLessonsPerDay] = useState(profile?.dailyLessonLimit || 5);
  const [dictionaryId, setDictionaryId] = useState<number | null>(profile?.dictionaryId || null);
  
  const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadDictionaries();
  }, []);

  const loadDictionaries = async () => {
    try {
      const response = await api.dictionaries.list();
      setDictionaries(response.dictionaries);
      
      // Если словарь не выбран, выбираем первый
      if (!dictionaryId && response.dictionaries.length > 0) {
        setDictionaryId(response.dictionaries[0].id);
      }
    } catch (err) {
      console.error('Failed to load dictionaries:', err);
      setError('Не удалось загрузить список словарей');
    }
  };

  const handleSave = async () => {
    if (!dictionaryId) {
      setError('Выберите словарь');
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await api.settings.update({
        level,
        words_per_lesson: wordsPerLesson,
        lessons_per_day: lessonsPerDay,
        dictionary_id: dictionaryId,
      });

      setSuccess('Настройки успешно сохранены');
      
      // Обновляем профиль в store
      if (profile) {
        useStore.setState({
          profile: {
            ...profile,
            level,
            wordsPerLesson,
            dailyLessonLimit: lessonsPerDay,
            dictionaryId,
          }
        });
      }

      // Возвращаемся на дашборд через 1 секунду
      setTimeout(() => navigate('/dashboard'), 1000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      setError(err.detail || 'Не удалось сохранить настройки');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 text-gray-500 hover:text-gray-700 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="font-semibold text-gray-800">Настройки</h1>
        </div>
      </div>

      <div className="max-w-lg mx-auto p-4 space-y-6">
        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-xl">
            {success}
          </div>
        )}

        {/* Level */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-indigo-100 p-2 rounded-lg">
              <User className="w-5 h-5 text-indigo-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Уровень знания</h2>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {['A1', 'A2', 'B1', 'B2'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setLevel(lvl as Level)}
                className={`p-4 rounded-xl border-2 transition ${
                  level === lvl
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-semibold text-gray-800">{lvl}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {lvl === 'A1' && 'Начальный'}
                  {lvl === 'A2' && 'Элементарный'}
                  {lvl === 'B1' && 'Средний'}
                  {lvl === 'B2' && 'Продвинутый'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Words per lesson */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-green-100 p-2 rounded-lg">
              <BookOpen className="w-5 h-5 text-green-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Слов в уроке</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="3"
              max="15"
              value={wordsPerLesson}
              onChange={(e) => setWordsPerLesson(parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
            />
            <div className="text-2xl font-bold text-green-600 w-12 text-center">
              {wordsPerLesson}
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            От 3 до 15 слов в одном уроке
          </p>
        </div>

        {/* Lessons per day */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Уроков в день</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="1"
              max="10"
              value={lessonsPerDay}
              onChange={(e) => setLessonsPerDay(parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="text-2xl font-bold text-purple-600 w-12 text-center">
              {lessonsPerDay}
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            От 1 до 10 уроков в день
          </p>
        </div>

        {/* Dictionary */}
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Target className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Словарь</h2>
          </div>
          
          <div className="space-y-2">
            {dictionaries.map((dict) => (
              <button
                key={dict.id}
                onClick={() => setDictionaryId(dict.id)}
                className={`w-full p-4 rounded-xl border-2 text-left transition ${
                  dictionaryId === dict.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-gray-800">{dict.name}</div>
                    {dict.description && (
                      <div className="text-xs text-gray-500 mt-1">{dict.description}</div>
                    )}
                  </div>
                  <div className="text-xs text-gray-400">{dict.total_words} слов</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Save button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Сохранение...
            </>
          ) : (
            <>
              <Save className="w-5 h-5" />
              Сохранить настройки
            </>
          )}
        </button>
      </div>
    </div>
  );
}
