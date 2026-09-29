import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { BookOpen, Trash2, Edit2, Eye, LogOut, Plus } from 'lucide-react';

interface Dictionary {
  id: number;
  name: string;
  description: string | null;
  category: string;
  words_count: number;
}

export default function AdminDictionariesPage() {
  const navigate = useNavigate();
  const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Проверяем наличие токена
    const token = localStorage.getItem('admin_token');
    if (!token) {
      navigate('/admin/login');
      return;
    }
    loadDictionaries();
  }, [navigate]);

  const loadDictionaries = async () => {
    try {
      setLoading(true);
      const data = await api.admin.getDictionaries();
      setDictionaries(data);
    } catch (err: any) {
      if (err.status === 401) {
        localStorage.removeItem('admin_token');
        navigate('/admin/login');
      } else {
        setError(err.detail || 'Ошибка загрузки словарей');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Вы уверены, что хотите удалить словарь "${name}"?\n\nЭто действие нельзя отменить. Все связи словаря со словами будут удалены.`)) {
      return;
    }

    try {
      const response = await api.admin.deleteDictionary(id);
      
      if (response.affected_users > 0) {
        alert(
          `Словарь "${name}" удален.\n\n` +
          `⚠️ Внимание: ${response.affected_users} пользователь(ей) использовали этот словарь.\n` +
          `Их активный словарь сброшен. Им нужно выбрать новый словарь в настройках.`
        );
      } else {
        alert(`Словарь "${name}" успешно удален.`);
      }
      
      setDictionaries(dictionaries.filter(d => d.id !== id));
    } catch (err: any) {
      alert(err.detail || 'Ошибка удаления словаря');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    navigate('/admin/login');
  };

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      general: '📚 Общий',
      it: '💻 IT',
      travel: '✈️ Путешествия',
      business: '💼 Бизнес',
      food: '🍽️ Еда',
      medical: '🏥 Медицина',
      daily: '💬 Повседневное',
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-purple-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Управление словарями</h1>
              <p className="text-sm text-gray-600">Админ-панель</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Выйти
          </button>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">Всего словарей</div>
            <div className="text-3xl font-bold text-gray-900">{dictionaries.length}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">Всего слов</div>
            <div className="text-3xl font-bold text-gray-900">
              {dictionaries.reduce((sum, d) => sum + d.words_count, 0)}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">Категорий</div>
            <div className="text-3xl font-bold text-gray-900">
              {new Set(dictionaries.map(d => d.category)).size}
            </div>
          </div>
        </div>

        {/* Dictionaries List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Список словарей</h2>
          </div>

          {dictionaries.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              Словари не найдены
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {dictionaries.map((dict) => (
                <div key={dict.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{dict.name}</h3>
                        <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                          {getCategoryLabel(dict.category)}
                        </span>
                      </div>
                      {dict.description && (
                        <p className="text-sm text-gray-600 mb-2">{dict.description}</p>
                      )}
                      <p className="text-sm text-gray-500">
                        Слов: <span className="font-medium text-gray-700">{dict.words_count}</span>
                      </p>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => navigate(`/admin/dictionaries/${dict.id}`)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Просмотреть слова"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => navigate(`/admin/dictionaries/${dict.id}/edit`)}
                        className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Редактировать"
                      >
                        <Edit2 className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(dict.id, dict.name)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
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
