import { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, CheckCircle, XCircle, HelpCircle, Loader2 } from 'lucide-react';

export default function ExercisePage() {
  const navigate = useNavigate();
  const {
    currentLesson, currentExerciseIndex, exerciseDraft,
    submitExerciseTranslation, evaluateExercise, nextExercise,
    completeLesson, abandonLesson, setExerciseDraft, isLoading, error, clearError
  } = useStore();

  const [showResult, setShowResult] = useState(false);
  const [currentResult, setCurrentResult] = useState<string | null>(null);
  const [showAbandonModal, setShowAbandonModal] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [resultData, setResultData] = useState<any>(null);

  // Load current lesson if not in store
  useEffect(() => {
    const loadLesson = async () => {
      console.log('🔍 ExercisePage: checking current lesson...');
      console.log('   currentLesson:', currentLesson);
      
      if (!currentLesson || currentLesson.status !== 'in_progress') {
        console.log('   No lesson in store, loading from backend...');
        const lesson = await useStore.getState().loadCurrentLesson();
        
        if (!lesson) {
          console.log('   No lesson found, redirecting to dashboard');
          navigate('/dashboard');
        } else {
          console.log('   Lesson loaded successfully');
        }
      } else {
        console.log('   Lesson found in store');
      }
    };
    
    loadLesson();
  }, []);

  // Block navigation
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = '';
    };

    const handlePopState = () => {
      setShowLeaveModal(true);
      window.history.pushState(null, '', window.location.href);
    };

    window.history.pushState(null, '', window.location.href);
    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  if (!currentLesson) return null;

  const exercise = currentLesson.exercises[currentExerciseIndex];
  if (!exercise) return null;

  const progress = ((currentExerciseIndex) / currentLesson.exercises.length) * 100;
  const isLastExercise = currentExerciseIndex === currentLesson.exercises.length - 1;

  const handleSubmit = async () => {
    if (!exerciseDraft.trim()) return;
    
    try {
      const result = await evaluateExercise(parseInt(exercise.id), exerciseDraft);
      setCurrentResult(result.result);
      setResultData(result);
      setShowResult(true);
    } catch (error: any) {
      console.error('Failed to evaluate:', error);
      // Показываем понятное сообщение пользователю
      if (error.status === 503) {
        alert('Сервис временно недоступен. Попробуйте позже. Ваш перевод сохранён.');
      } else {
        alert(`Ошибка: ${error.detail || 'Не удалось проверить перевод'}`);
      }
    }
  };

  const handleDontKnow = async () => {
    try {
      const result = await evaluateExercise(parseInt(exercise.id), '');
      setCurrentResult('dont_know');
      setResultData(result);
      setShowResult(true);
    } catch (error: any) {
      console.error('Failed to evaluate:', error);
      // Показываем понятное сообщение пользователю
      if (error.status === 503) {
        alert('Сервис временно недоступен. Попробуйте позже.');
      } else {
        alert(`Ошибка: ${error.detail || 'Не удалось оценить упражнение'}`);
      }
    }
  };

  const handleNext = () => {
    setShowResult(false);
    setCurrentResult(null);
    setExerciseDraft('');
    setResultData(null);

    if (isLastExercise) {
      completeLesson();
      navigate('/lesson/summary');
    } else {
      nextExercise();
    }
  };

  const handleAbandon = async () => {
    try {
      await abandonLesson();
      setShowAbandonModal(false);
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to abandon:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-3 sticky top-0 z-10">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center justify-between mb-2">
            <button
              onClick={() => setShowAbandonModal(true)}
              className="text-sm text-gray-500 hover:text-red-500 transition"
            >
              Прервать
            </button>
            <span className="text-sm font-medium text-gray-600">
              {currentExerciseIndex + 1} / {currentLesson.exercises.length}
            </span>
            <div className="w-16" />
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 max-w-lg mx-auto w-full p-4 flex flex-col">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl text-sm mb-4">
            {error}
            <button onClick={clearError} className="ml-2 underline">Закрыть</button>
          </div>
        )}

        {!showResult ? (
          <div className="animate-fade-in flex flex-col flex-1">
            {/* Target words */}
            <div className="bg-indigo-50 rounded-xl p-4 mb-4 border border-indigo-100 animate-slide-up">
              <p className="text-xs text-indigo-600 uppercase tracking-wide mb-2 font-medium">Слова в упражнении</p>
              <div className="flex flex-wrap gap-2">
                {exercise.words
                  .filter(w => w.isTarget)
                  .map((w, idx) => (
                    <span
                      key={idx}
                      className="bg-white px-3 py-1.5 rounded-lg text-sm font-medium text-indigo-700 border border-indigo-200"
                    >
                      {w.surfaceForm}
                    </span>
                  ))}
              </div>
            </div>

            {/* Sentence */}
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6 animate-slide-up">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Переведите предложение</p>
              <p className="text-lg font-medium text-gray-800 leading-relaxed">
                {exercise.targetSentence}
              </p>
            </div>

            {/* Input */}
            <div className="flex-1">
              <textarea
                value={exerciseDraft}
                onChange={e => setExerciseDraft(e.target.value)}
                placeholder="Введите перевод на русский..."
                className="w-full h-32 p-4 border border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition text-gray-800"
                disabled={isLoading}
              />
            </div>

            {/* Actions */}
            <div className="mt-4 space-y-3">
              <button
                onClick={handleSubmit}
                disabled={!exerciseDraft.trim() || isLoading}
                className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-200"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Проверяем...
                  </>
                ) : (
                  'Проверить'
                )}
              </button>

              <button
                onClick={handleDontKnow}
                disabled={isLoading}
                className="w-full py-3 bg-gray-100 text-gray-600 font-medium rounded-xl hover:bg-gray-200 transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <HelpCircle className="w-5 h-5" />
                Не знаю
              </button>
            </div>
          </div>
        ) : (
          /* Result view */
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-slide-up">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 ${
              currentResult === 'correct' ? 'bg-green-100' :
              currentResult === 'typo' ? 'bg-amber-100' :
              'bg-red-100'
            }`}>
              {currentResult === 'correct' && <CheckCircle className="w-10 h-10 text-green-600" />}
              {currentResult === 'typo' && <AlertTriangle className="w-10 h-10 text-amber-600" />}
              {(currentResult === 'incorrect' || currentResult === 'dont_know') && <XCircle className="w-10 h-10 text-red-600" />}
            </div>

            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {currentResult === 'correct' && 'Правильно!'}
              {currentResult === 'typo' && 'Почти! Опечатка'}
              {currentResult === 'incorrect' && 'Неверно'}
              {currentResult === 'dont_know' && 'Не беда!'}
            </h2>

            <p className="text-gray-500 mb-6">
              {currentResult === 'correct' && 'Слово запомнится лучше в следующий раз'}
              {currentResult === 'typo' && 'Маленькая ошибка, но смысл верный'}
              {currentResult === 'incorrect' && 'Это слово встретится снова'}
              {currentResult === 'dont_know' && 'Мы повторим это слово позже'}
            </p>

            {/* Show correct answer */}
            {resultData && (
              <div className="bg-white rounded-xl p-4 border border-gray-200 w-full mb-6">
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Правильный перевод</p>
                <p className="text-gray-800 font-medium">{resultData.referenceTranslation}</p>
              </div>
            )}

            {/* Show new suggested words */}
            {resultData && resultData.newSuggestedWords && resultData.newSuggestedWords.length > 0 && (
              <div className="bg-blue-50 rounded-xl p-4 border border-blue-200 w-full mb-6">
                <p className="text-xs text-blue-600 uppercase tracking-wide mb-2 font-medium">💡 Слова для изучения</p>
                <p className="text-sm text-blue-700 mb-2">Эти слова встретились в предложении, но вы их не перевели:</p>
                <div className="flex flex-wrap gap-2">
                  {resultData.newSuggestedWords.map((word: string, idx: number) => (
                    <span
                      key={idx}
                      className="bg-white px-3 py-1.5 rounded-lg text-sm font-medium text-blue-700 border border-blue-200"
                    >
                      {word}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-blue-600 mt-2">Они будут добавлены в ваш словарь для повторения</p>
              </div>
            )}

            <button
              onClick={handleNext}
              className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition shadow-lg shadow-indigo-200"
            >
              {isLastExercise ? 'Завершить урок' : 'Далее'}
            </button>
          </div>
        )}
      </div>

      {/* Abandon Modal */}
      {showAbandonModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Прервать урок?</h3>
            <p className="text-gray-500 text-sm mb-6">Прогресс текущего урока не будет сохранён. Лимит уроков на сегодня не вернётся.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowAbandonModal(false)}
                className="flex-1 py-3 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition"
              >
                Отмена
              </button>
              <button
                onClick={handleAbandon}
                className="flex-1 py-3 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 transition"
              >
                Прервать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Leave Modal */}
      {showLeaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Покинуть урок?</h3>
            <p className="text-gray-500 text-sm mb-6">Ваш текущий ввод будет сохранён. Вы сможете вернуться к уроку позже.</p>
            <div className="flex gap-3">
              <button
                onClick={() => { setShowLeaveModal(false); navigate('/dashboard'); }}
                className="flex-1 py-3 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 transition"
              >
                Выйти
              </button>
              <button
                onClick={() => setShowLeaveModal(false)}
                className="flex-1 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition"
              >
                Остаться
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
