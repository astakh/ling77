import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import { ArrowLeft, BookOpen } from 'lucide-react';

interface Dictionary {
  id: number;
  name: string;
  description: string | null;
  category: string;
}

interface Word {
  id: number;
  lemma: string;
  pos: string;
  level: string;
  translations: string[];
}

export default function AdminDictionaryWordsPage() {
  const navigate = useNavigate();
  const { dictionaryId } = useParams<{ dictionaryId: string }>();
  const [dictionary, setDictionary] = useState<Dictionary | null>(null);
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!dictionaryId) {
      navigate('/admin/dictionaries');
      return;
    }
    loadData();
  }, [dictionaryId, navigate]);

  const loadData = async () => {
    try {
      setLoading(true);
      const id = parseInt(dictionaryId!);
      const [dictData, wordsData] = await Promise.all([
        api.admin.getDictionary(id),
        api.admin.getDictionaryWords(id),
      ]);
      setDictionary(dictData);
      setWords(wordsData);
    } catch (err: any) {
      if (err.status === 401) {
        localStorage.removeItem('admin_token');
        navigate('/admin/login');
      } else {
        setError(err.detail || 'Ошибка загрузки данных');
      }
    } finally {
      setLoading(false);
    }
  };

  const filteredWords = words.filter(word => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      word.lemma.toLowerCase().includes(query) ||
      word.translations.some(t => t.toLowerCase().includes(query))
    );
  });

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      A1: 'bg-green-100 text-green-700',
      A2: 'bg-blue-100 text-blue-700',
      B1: 'bg-purple-100 text-purple-700',
      B2: 'bg-orange-100 text-orange-700',
    };
    return colors[level] || 'bg-gray-100 text-gray-700';
  };

  const getPosLabel = (pos: string) => {
    const labels: Record<string, string> = {
      noun: 'сущ.',
      verb: 'гл.',
      adjective: 'прил.',
      adverb: 'нар.',
    };
    return labels[pos] || pos;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  if (!dictionary) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Словарь не найден</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/admin/dictionaries')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Назад к списку словарей
          </button>
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-purple-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{dictionary.name}</h1>
              {dictionary.description && (
                <p className="text-sm text-gray-600 mt-1">{dictionary.description}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="text-sm text-gray-600 mb-1">Всего слов в словаре</div>
          <div className="text-3xl font-bold text-gray-900">{words.length}</div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск по слову или переводу..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Words List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Слова ({filteredWords.length} из {words.length})
            </h2>
          </div>

          {filteredWords.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              {searchQuery ? 'Слова не найдены' : 'В словаре нет слов'}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredWords.map((word) => (
                <div key={word.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{word.lemma}</h3>
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                          {getPosLabel(word.pos)}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelColor(word.level)}`}>
                          {word.level}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {word.translations.map((translation, idx) => (
                          <span key={idx} className="text-sm text-gray-600">
                            {translation}
                            {idx < word.translations.length - 1 && ','}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
