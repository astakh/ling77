import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { ArrowLeft, BookOpen, Check, Search, Loader2, RefreshCw } from 'lucide-react';

interface Dictionary {
  id: number;
  name: string;
  description: string | null;
  category: string;
  total_words: number;
  levels: string[];
  level_counts: Record<string, number>;
  created_at: string;
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

export default function DictionariesPage() {
  const navigate = useNavigate();
  const { profile } = useStore();
  const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
  const [currentDictId, setCurrentDictId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [changing, setChanging] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [dictsRes, currentRes] = await Promise.all([
        api.dictionaries.list(filterCategory || undefined, search || undefined),
        api.dictionaries.getCurrent().catch(err => {
          // 400 means no profile yet - that's ok
          if (err.status === 400) {
            return { dictionary: null };
          }
          throw err;
        }),
      ]);
      setDictionaries(dictsRes.dictionaries);
      setCurrentDictId(currentRes.dictionary?.id || null);
    } catch (e: any) {
      setError(e.detail || 'Ошибка загрузки словарей');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterCategory, search]);

  const handleChangeDictionary = async (dictId: number, dictName: string) => {
    if (dictId === currentDictId) return;

    if (!confirm(`Сменить словарь на "${dictName}"?\n\nНовые уроки будут использовать слова из этого словаря. Ранее изученные слова сохранятся.`)) {
      return;
    }

    setChanging(dictId);
    setSuccess('');
    setError('');
    try {
      const result = await api.dictionaries.change(dictId);
      setCurrentDictId(result.dictionary_id);
      setSuccess(`Словарь изменён на "${result.dictionary_name}"`);

      // Update profile in store
      if (profile) {
        useStore.setState({
          profile: { ...profile, dictionaryId: result.dictionary_id }
        });
      }
    } catch (e: any) {
      setError(e.detail || 'Ошибка смены словаря');
    } finally {
      setChanging(null);
    }
  };

  const filteredDicts = dictionaries.filter(d => {
    if (search && !d.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (filterCategory && d.category !== filterCategory) return false;
    return true;
  });

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
          <h1 className="font-semibold text-gray-800">Мои словари</h1>
          <button
            onClick={loadData}
            className="p-2 text-gray-500 hover:text-indigo-600 transition"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="max-w-lg mx-auto p-4 space-y-4">
        {/* Current dictionary */}
        {currentDictId && (
          <div className="bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl p-5 text-white shadow-lg">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-3 rounded-xl">
                <BookOpen className="w-7 h-7" />
              </div>
              <div className="flex-1">
                <div className="text-xs text-white/80 uppercase tracking-wide">Активный словарь</div>
                <div className="font-semibold text-lg">
                  {dictionaries.find(d => d.id === currentDictId)?.name || 'Загрузка...'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 p-3 rounded-xl text-sm">
            {success}
          </div>
        )}

        {/* Search & Filters */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Поиск словаря..."
              className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
            />
          </div>

          <div className="flex gap-2 overflow-x-auto pb-1">
            {[
              { value: '', label: 'Все' },
              { value: 'general', label: '📚 Общий' },
              { value: 'it', label: '💻 IT' },
              { value: 'travel', label: '✈️ Путешествия' },
              { value: 'business', label: '💼 Бизнес' },
              { value: 'food', label: '🍽️ Еда' },
              { value: 'medical', label: '🏥 Медицина' },
              { value: 'daily', label: '💬 Повседневное' },
            ].map(f => (
              <button
                key={f.value}
                onClick={() => setFilterCategory(f.value)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                  filterCategory === f.value
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'bg-white text-gray-500 border border-gray-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Dictionaries list */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
          </div>
        ) : filteredDicts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📚</div>
            <p className="text-gray-500">Словари не найдены</p>
            <p className="text-sm text-gray-400 mt-2">
              Обратитесь к администратору для добавления словарей
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredDicts.map(dict => {
              const isActive = dict.id === currentDictId;
              const isChanging = changing === dict.id;

              return (
                <div
                  key={dict.id}
                  className={`bg-white rounded-xl p-4 border transition ${
                    isActive ? 'border-indigo-300 ring-2 ring-indigo-100' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-800">{dict.name}</h3>
                        {isActive && (
                          <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Check className="w-3 h-3" />
                            активен
                          </span>
                        )}
                      </div>
                      {dict.description && (
                        <p className="text-sm text-gray-500 mb-2">{dict.description}</p>
                      )}
                      <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                        <span>{dict.total_words} слов</span>
                        <span>•</span>
                        <span className="bg-gray-100 px-2 py-0.5 rounded">
                          {CATEGORY_LABELS[dict.category] || dict.category}
                        </span>
                        {Object.keys(dict.level_counts).length > 0 && (
                          <>
                            <span>•</span>
                            <div className="flex gap-1">
                              {dict.levels.sort().map(level => (
                                <span
                                  key={level}
                                  className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded"
                                >
                                  {level}: {dict.level_counts[level]}
                                </span>
                              ))}
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => handleChangeDictionary(dict.id, dict.name)}
                      disabled={isActive || isChanging}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                        isActive
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : isChanging
                          ? 'bg-indigo-100 text-indigo-400'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      }`}
                    >
                      {isChanging ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : isActive ? (
                        'Текущий'
                      ) : (
                        'Выбрать'
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
          <p className="font-medium mb-1">💡 Как работают словари</p>
          <p className="text-blue-700">
            Словарь определяет набор слов, которые будут использоваться в новых уроках.
            Смена словаря не влияет на уже изученные слова — они остаются в вашем личном словаре.
          </p>
        </div>
      </div>
    </div>
  );
}
