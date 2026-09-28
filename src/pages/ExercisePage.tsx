import { useState, useEffect, useCallback } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { getWordById } from '../data/words';
import { AlertTriangle, CheckCircle, XCircle, HelpCircle, Loader2, Eye } from 'lucide-react';

export default function ExercisePage() {
  const navigate = useNavigate();
  const {
    currentLesson, currentExerciseIndex, exerciseDraft,
    submitExerciseTranslation, evaluateExercise, nextExercise,
    completeLesson, abandonLesson, setExerciseDraft
  } = useStore();

  const [showTranslation, setShowTranslation] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [currentResult, setCurrentResult] = useState<'correct' | 'typo' | 'incorrect' | 'dont_know' | null>(null);
  const [showAbandonModal, setShowAbandonModal] = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);

  // Redirect if no lesson
  useEffect(() => {
    if (!currentLesson || currentLesson.status !== 'in_progress') {
      navigate('/dashboard');
    }
  }, [currentLesson, navigate]);

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

  // Load draft from localStorage
  useEffect(() => {
    const draft = localStorage.getItem('lw_exercise_draft');
    if (draft && currentLesson) {
      setExerciseDraft(draft);
    }
  }, [currentExerciseIndex, setExerciseDraft, currentLesson]);

  if (!currentLesson) return null;

  const exercise = currentLesson.exercises[currentExerciseIndex];
  if (!exercise) return null;

  const progress = ((currentExerciseIndex) / currentLesson.exercises.length) * 100;
  const isLastExercise = currentExerciseIndex === currentLesson.exercises.length - 1;
  const isEvaluated = exercise.status === 'evaluated';

  const targetWords = exercise.words.filter(w => w.isTarget).map(w => getWordById(w.wordId));

  const handleSubmit = () => {
    if (!exerciseDraft.trim()) return;
    submitExerciseTranslation(exerciseDraft);

    setIsEvaluating(true);
    // Simulate LLM evaluation delay
    setTimeout(() => {
      // Simple mock evaluation: check if user translation contains any target word translations
      const translation = exerciseDraft.toLowerCase();
      let result: 'correct' | 'typo' | 'incorrect' = 'incorrect';

      const hasCorrectTranslation = targetWords.some(w =>
        w && w.translations.some(t => translation.includes(t.toLowerCase()))
      );

      if (hasCorrectTranslation) {
        result = 'correct';
      } else {
        // Check for typos (partial match)
        const hasPartialMatch = targetWords.some(w =>
          w && w.translations.some(t => {
            const tLower = t.toLowerCase();
            return tLower.length > 3 && translation.split('').filter(c => tLower.includes(c)).length > tLower.length * 0.6;
          })
        );
        if (hasPartialMatch) {
          result = 'typo';
        }
      }

      setCurrentResult(result);
      evaluateExercise(result);
      setIsEvaluating(false);
      setShowResult(true);
    }, 1500);
  };

  const handleDontKnow = () => {
    setCurrentResult('dont_know');
    evaluateExercise('dont_know');
    setShowResult(true);
  };

  const handleNext = useCallback(() => {
    setShowResult(false);
    setCurrentResult(null);
    setShowTranslation(false);
    setExerciseDraft('');
    localStorage.removeItem('lw_exercise_draft');

    if (isLastExercise) {
      completeLesson();
      navigate('/lesson/summary');
    } else {
      nextExercise();
    }
  }, [isLastExercise, completeLesson, navigate, nextExercise, setExerciseDraft]);

  const handleAbandon = () => {
    abandonLesson();
    setShowAbandonModal(false);
    navigate('/dashboard');
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
            <div className="w-16" /> {/* spacer */}
          </div>
          {/* Progress bar */}
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
        {!showResult ? (
          <div className="animate-fade-in flex flex-col flex-1">
            {/* Sentence */}
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6 animate-slide-up">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-2">Переведите предложение</p>
              <p className="text-lg font-medium text-gray-800 leading-relaxed">
                {exercise.targetSentence}
              </p>

              {/* Target words hint */}
              <div className="mt-4 flex flex-wrap gap-2">
                {targetWords.map((w, i) => w && (
                  <span key={i} className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-lg">
                    {w.lemma} — {w.translations[0]}
                  </span>
                ))}
              </div>
            </div>

            {/* Reference translation toggle */}
            <button
              onClick={() => setShowTranslation(!showTranslation)}
              className="flex items-center gap-2 text-sm text-gray-500 hover:text-indigo-600 mb-4 transition"
            >
              <Eye className="w-4 h-4" />
              {showTranslation ? 'Скрыть перевод' : 'Показать перевод-подсказку'}
            </button>

            {showTranslation && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
                <p className="text-sm text-amber-800">{exercise.referenceTranslation}</p>
              </div>
            )}

            {/* Input */}
            <div className="flex-1">
              <textarea
                value={exerciseDraft}
                onChange={e => {
                  setExerciseDraft(e.target.value);
                  localStorage.setItem('lw_exercise_draft', e.target.value);
                }}
                placeholder="Введите перевод на русский..."
                className="w-full h-32 p-4 border border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition text-gray-800"
                disabled={isEvaluating}
              />
            </div>

            {/* Actions */}
            <div className="mt-4 space-y-3">
              <button
                onClick={handleSubmit}
                disabled={!exerciseDraft.trim() || isEvaluating}
                className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-200"
              >
                {isEvaluating ? (
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
                disabled={isEvaluating}
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
            <div className="bg-white rounded-xl p-4 border border-gray-200 w-full mb-6">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Правильный перевод</p>
              <p className="text-gray-800 font-medium">{exercise.referenceTranslation}</p>
            </div>

            {/* Target words review */}
            <div className="w-full space-y-2 mb-6">
              {exercise.words.filter(w => w.isTarget).map((ew, i) => {
                const word = getWordById(ew.wordId);
                if (!word) return null;
                return (
                  <div key={i} className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-100">
                    <div>
                      <span className="font-medium text-gray-800">{word.lemma}</span>
                      <span className="text-gray-500 text-sm ml-2">{word.translations[0]}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      {ew.stageAfter > ew.stageBefore && (
                        <span className="text-xs text-green-600 font-medium">↑{ew.stageAfter - ew.stageBefore}</span>
                      )}
                      {ew.stageAfter < ew.stageBefore && (
                        <span className="text-xs text-red-600 font-medium">↓{ew.stageBefore - ew.stageAfter}</span>
                      )}
                      <span className="text-xs text-gray-400">ст.{ew.stageAfter}</span>
                    </div>
                  </div>
                );
              })}
            </div>

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
