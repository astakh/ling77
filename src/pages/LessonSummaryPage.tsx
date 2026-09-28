import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { getWordById } from '../data/words';
import { Trophy, ArrowRight, Flame, Star } from 'lucide-react';

export default function LessonSummaryPage() {
  const navigate = useNavigate();
  const { currentLesson, streak } = useStore();

  if (!currentLesson || currentLesson.status !== 'completed') {
    navigate('/dashboard');
    return null;
  }

  const totalExercises = currentLesson.exercises.length;
  const correctCount = currentLesson.exercises.filter(e =>
    e.words.some(w => w.isTarget && w.result === 'correct')
  ).length;
  const typoCount = currentLesson.exercises.filter(e =>
    e.words.some(w => w.isTarget && w.result === 'typo')
  ).length;
  const incorrectCount = currentLesson.exercises.filter(e =>
    e.words.some(w => w.isTarget && (w.result === 'incorrect' || w.result === 'dont_know'))
  ).length;

  const allWords = currentLesson.exercises.flatMap(e => e.words.filter(w => w.isTarget));
  const newWordsLearned = allWords.filter(w => w.isNew && w.stageAfter > 0).length;
  const wordsReviewed = allWords.filter(w => !w.isNew).length;

  const accuracy = totalExercises > 0 ? Math.round(((correctCount + typoCount) / totalExercises) * 100) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col">
      <div className="flex-1 max-w-lg mx-auto w-full p-4 flex flex-col items-center justify-center">
        {/* Trophy */}
        <div className="bg-gradient-to-br from-yellow-400 to-orange-500 w-24 h-24 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-orange-200">
          <Trophy className="w-12 h-12 text-white" />
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-2">Урок завершён!</h1>
        <p className="text-gray-500 mb-8">Урок #{currentLesson.lessonNumber}</p>

        {/* Stats */}
        <div className="w-full grid grid-cols-2 gap-3 mb-6">
          <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
            <div className="text-3xl font-bold text-indigo-600">{accuracy}%</div>
            <div className="text-xs text-gray-500 mt-1">Точность</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-1">
              <Flame className="w-5 h-5 text-orange-500" />
              <span className="text-3xl font-bold text-gray-800">{streak.count}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Стрик</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-1">
              <Star className="w-5 h-5 text-green-500" />
              <span className="text-3xl font-bold text-gray-800">{newWordsLearned}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Новых слов</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-gray-100 text-center">
            <div className="text-3xl font-bold text-gray-800">{wordsReviewed}</div>
            <div className="text-xs text-gray-500 mt-1">Повторено</div>
          </div>
        </div>

        {/* Results breakdown */}
        <div className="w-full bg-white rounded-xl p-4 border border-gray-100 mb-6">
          <h3 className="font-medium text-gray-700 mb-3">Результаты</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-sm text-gray-600">Правильно</span>
              </div>
              <span className="font-medium text-gray-800">{correctCount}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-sm text-gray-600">Опечатки</span>
              </div>
              <span className="font-medium text-gray-800">{typoCount}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm text-gray-600">Ошибки</span>
              </div>
              <span className="font-medium text-gray-800">{incorrectCount}</span>
            </div>
          </div>
        </div>

        {/* Words summary */}
        <div className="w-full bg-white rounded-xl p-4 border border-gray-100 mb-8">
          <h3 className="font-medium text-gray-700 mb-3">Слова в уроке</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {allWords.map((ew, i) => {
              const word = getWordById(ew.wordId);
              if (!word) return null;
              return (
                <div key={i} className="flex items-center justify-between py-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      ew.result === 'correct' ? 'bg-green-500' :
                      ew.result === 'typo' ? 'bg-amber-500' : 'bg-red-500'
                    }`} />
                    <span className="text-sm font-medium text-gray-700">{word.lemma}</span>
                    <span className="text-xs text-gray-400">{word.translations[0]}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {ew.stageBefore}→{ew.stageAfter}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <button
          onClick={() => navigate('/dashboard')}
          className="w-full py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2 shadow-lg shadow-indigo-200"
        >
          На главную
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
