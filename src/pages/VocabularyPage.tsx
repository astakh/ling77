import { useState } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { getWordById } from '../data/words';
import { ArrowLeft, Search, Filter } from 'lucide-react';
import { WordStatus } from '../types';

const STATUS_LABELS: Record<WordStatus, string> = {
  active: 'Изучаю',
  mastered: 'Выучено',
  ignored: 'Игнор',
};

const STATUS_COLORS: Record<WordStatus, string> = {
  active: 'bg-blue-100 text-blue-700',
  mastered: 'bg-green-100 text-green-700',
  ignored: 'bg-gray-100 text-gray-500',
};

export default function VocabularyPage() {
  const navigate = useNavigate();
  const { profile, updateWordStatus } = useStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | WordStatus>('all');
  const [showFilter, setShowFilter] = useState(false);

  if (!profile) {
    navigate('/dashboard');
    return null;
  }

  const filteredWords = profile.userWords
    .map((uw, idx) => ({ ...uw, index: idx }))
    .filter(uw => {
      if (filter !== 'all' && uw.status !== filter) return false;
      if (search) {
        const word = getWordById(uw.wordId);
        if (!word) return false;
        const searchLower = search.toLowerCase();
        return (
          word.lemma.toLowerCase().includes(searchLower) ||
          word.translations.some(t => t.toLowerCase().includes(searchLower))
        );
      }
      return true;
    })
    .sort((a, b) => {
      // Sort: active first, then by stage
      if (a.status === 'active' && b.status !== 'active') return -1;
      if (a.status !== 'active' && b.status === 'active') return 1;
      return a.stage - b.stage;
    });

  const cycleStatus = (index: number, currentStatus: WordStatus) => {
    const nextStatus: WordStatus = currentStatus === 'active' ? 'mastered' : currentStatus === 'mastered' ? 'ignored' : 'active';
    updateWordStatus(index, nextStatus);
  };

  const counts = {
    all: profile.userWords.length,
    active: profile.userWords.filter(uw => uw.status === 'active').length,
    mastered: profile.userWords.filter(uw => uw.status === 'mastered').length,
    ignored: profile.userWords.filter(uw => uw.status === 'ignored').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 text-gray-500 hover:text-gray-700 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="font-semibold text-gray-800">Мой словарь</h1>
          <div className="w-9" />
        </div>
      </div>

      <div className="max-w-lg mx-auto p-4">
        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Поиск слова..."
            className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-1">
          <button
            onClick={() => setShowFilter(!showFilter)}
            className="flex items-center gap-1 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition"
          >
            <Filter className="w-4 h-4" />
            Фильтр
          </button>
          {(['all', 'active', 'mastered', 'ignored'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                filter === f ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-500 border border-gray-200'
              }`}
            >
              {f === 'all' ? 'Все' : STATUS_LABELS[f]} ({counts[f]})
            </button>
          ))}
        </div>

        {/* Word list */}
        {filteredWords.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📖</div>
            <p className="text-gray-500">
              {profile.userWords.length === 0
                ? 'Словарь пуст. Начните уроки, чтобы добавить слова!'
                : 'Ничего не найдено'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredWords.map(uw => {
              const word = getWordById(uw.wordId);
              if (!word) return null;
              return (
                <div key={uw.wordId} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-800">{word.lemma}</span>
                        <span className="text-xs text-gray-400">{word.pos}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[uw.status]}`}>
                          {STATUS_LABELS[uw.status]}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        {word.translations.join(', ')}
                      </div>
                      <div className="flex items-center gap-3 mt-2">
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-gray-400">Стадия:</span>
                          <div className="flex gap-0.5">
                            {[0, 1, 2, 3, 4, 5, 6].map(s => (
                              <div
                                key={s}
                                className={`w-2 h-2 rounded-full ${
                                  s <= uw.stage ? 'bg-indigo-500' : 'bg-gray-200'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        {uw.dueLessonNumber !== null && (
                          <span className="text-xs text-gray-400">
                            Повтор: урок #{uw.dueLessonNumber}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => cycleStatus(uw.index, uw.status)}
                      className="text-xs px-2 py-1 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                    >
                      Сменить
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
