import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { ArrowLeft, Search, Filter, Loader2 } from 'lucide-react';
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

interface VocabWord {
  id: number;
  word_id: number;
  lemma: string;
  pos: string;
  translations: string[];
  status: WordStatus;
  stage: number;
  due_lesson_number: number | null;
}

export default function VocabularyPage() {
  const navigate = useNavigate();
  const { updateWordStatus } = useStore();
  const [words, setWords] = useState<VocabWord[]>([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | WordStatus>('all');
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadVocabulary();
  }, [filter, search, page]);

  const loadVocabulary = async () => {
    setLoading(true);
    try {
      const response = await api.vocabulary.list(page, 20, filter === 'all' ? undefined : filter, search || undefined);
      setWords(response.words);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load vocabulary:', error);
    } finally {
      setLoading(false);
    }
  };

  const cycleStatus = async (userWordId: number, currentStatus: WordStatus) => {
    const nextStatus: WordStatus = currentStatus === 'active' ? 'mastered' : currentStatus === 'mastered' ? 'ignored' : 'active';
    try {
      await updateWordStatus(userWordId, nextStatus);
      // Reload vocabulary
      await loadVocabulary();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
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
          {(['all', 'active', 'mastered', 'ignored'] as const).map(f => (
            <button
              key={f}
              onClick={() => { setFilter(f); setPage(1); }}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                filter === f ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-gray-500 border border-gray-200'
              }`}
            >
              {f === 'all' ? 'Все' : STATUS_LABELS[f]}
            </button>
          ))}
        </div>

        {/* Word list */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
          </div>
        ) : words.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📖</div>
            <p className="text-gray-500">
              {total === 0
                ? 'Словарь пуст. Начните уроки, чтобы добавить слова!'
                : 'Ничего не найдено'}
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              {words.map(word => (
                <div key={word.id} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-800">{word.lemma}</span>
                        <span className="text-xs text-gray-400">{word.pos}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[word.status]}`}>
                          {STATUS_LABELS[word.status]}
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
                                  s <= word.stage ? 'bg-indigo-500' : 'bg-gray-200'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        {word.due_lesson_number !== null && (
                          <span className="text-xs text-gray-400">
                            Повтор: урок #{word.due_lesson_number}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => cycleStatus(word.id, word.status)}
                      className="text-xs px-2 py-1 text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                    >
                      Сменить
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {total > 20 && (
              <div className="flex justify-center gap-2 mt-6">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-50"
                >
                  Назад
                </button>
                <span className="px-4 py-2 text-sm text-gray-600">
                  Страница {page} из {Math.ceil(total / 20)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= Math.ceil(total / 20)}
                  className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-50"
                >
                  Вперёд
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
