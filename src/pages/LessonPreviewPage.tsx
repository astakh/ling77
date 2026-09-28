import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, X, Play, RefreshCw } from 'lucide-react';
import { useState } from 'react';

export default function LessonPreviewPage() {
  const navigate = useNavigate();
  const { previewLesson, declineWord, startLesson, declinedWords, setDeclinedWords } = useStore();
  const [refreshing, setRefreshing] = useState(false);
  const preview = previewLesson();

  const handleDecline = (wordId: string) => {
    declineWord(wordId);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 300);
  };

  const handleStart = () => {
    startLesson();
    navigate('/lesson/exercise');
  };

  if (preview.words.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-4xl mb-4">📚</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Нет слов для урока</h2>
          <p className="text-gray-500 mb-6">Все слова текущего уровня уже добавлены или отклонены</p>
          <button
            onClick={() => { setDeclinedWords([]); navigate('/dashboard'); }}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium"
          >
            Сбросить отклонённые слова
          </button>
        </div>
      </div>
    );
  }

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
          <h1 className="font-semibold text-gray-800">Состав урока</h1>
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-500 hover:text-indigo-600 transition"
          >
            <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="max-w-lg mx-auto p-4">
        <p className="text-sm text-gray-500 mb-4">
          В этом уроке {preview.words.length} слов. Нажмите ✕ чтобы пропустить слово.
        </p>

        <div className="space-y-3 mb-6">
          {preview.words.map(word => (
            <div
              key={word.id}
              className={`bg-white rounded-xl p-4 border transition ${
                declinedWords.includes(word.id)
                  ? 'border-gray-100 opacity-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-800 text-lg">{word.lemma}</span>
                    {word.isNew && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">новое</span>
                    )}
                    {word.isDue && (
                      <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">повтор</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {word.translations.join(', ')}
                  </div>
                </div>
                {!declinedWords.includes(word.id) && (
                  <button
                    onClick={() => handleDecline(word.id)}
                    className="p-1.5 text-gray-400 hover:text-red-500 transition"
                    title="Пропустить слово"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleStart}
          className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-2xl hover:bg-indigo-700 transition flex items-center justify-center gap-3 shadow-lg shadow-indigo-200 text-lg"
        >
          <Play className="w-6 h-6" />
          Начать урок
        </button>
      </div>
    </div>
  );
}
