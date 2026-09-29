import { useNavigate } from 'react-router-dom';
import { BookOpen, Brain, Target, Zap, CheckCircle, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  const handleRegister = () => {
    navigate('/auth');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-indigo-600 rounded-2xl mb-6 shadow-lg">
            <BookOpen className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Кругослов
          </h1>
          <p className="text-2xl text-gray-600 mb-4">
            Учите английские слова эффективно
          </p>
          <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
            Интервальное повторение с использованием искусственного интеллекта. 
            Запоминайте слова в 3 раза быстрее благодаря научному подходу.
          </p>
          <button
            onClick={handleRegister}
            className="inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-xl hover:bg-indigo-700 transition shadow-lg shadow-indigo-200"
          >
            Начать бесплатно
            <ArrowRight className="w-5 h-5" />
          </button>
          <p className="text-sm text-gray-400 mt-4">
            Регистрация занимает 30 секунд
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4">
              <Brain className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Интервальное повторение
            </h3>
            <p className="text-gray-600">
              Научный метод запоминания. Слова повторяются именно тогда, когда вы готовы их забыть.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              AI-оценка переводов
            </h3>
            <p className="text-gray-600">
              Искусственный интеллект проверяет ваши переводы и дает мгновенную обратную связь.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Тематические словари
            </h3>
            <p className="text-gray-600">
              IT, бизнес, путешествия, еда — выбирайте слова, которые нужны именно вам.
            </p>
          </div>
        </div>

        {/* How it works */}
        <div className="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Как это работает
          </h2>
          <div className="space-y-8">
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                1
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Выберите словарь и уровень
                </h3>
                <p className="text-gray-600">
                  Определите свой уровень (A1-B2) и выберите тематический словарь, который вам интересен.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                2
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Проходите уроки каждый день
                </h3>
                <p className="text-gray-600">
                  Переводите предложения с английского на русский. AI проверяет ваши ответы и объясняет ошибки.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Запоминайте слова навсегда
                </h3>
                <p className="text-gray-600">
                  Система автоматически планирует повторения. Слова переходят в долгосрочную память.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Benefits */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Почему Кругослов?
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Научный подход</h3>
                <p className="text-gray-600">
                  Метод интервального повторения доказал свою эффективность в исследованиях.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Экономия времени</h3>
                <p className="text-gray-600">
                  Учите только те слова, которые действительно нужно повторить.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Персонализация</h3>
                <p className="text-gray-600">
                  Выбирайте словари по интересам: IT, бизнес, путешествия и другие.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Мгновенная обратная связь</h3>
                <p className="text-gray-600">
                  AI проверяет переводы и объясняет ошибки в реальном времени.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Отслеживание прогресса</h3>
                <p className="text-gray-600">
                  Видите статистику выученных слов и серий ежедневных занятий.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-bold text-gray-900 mb-1">Бесплатно</h3>
                <p className="text-gray-600">
                  Все функции доступны бесплатно. Без скрытых платежей.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="text-center bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">
            Готовы начать учить слова?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Присоединяйтесь к Кругослов сегодня и улучшите свой английский
          </p>
          <button
            onClick={handleRegister}
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 text-lg font-semibold rounded-xl hover:bg-gray-100 transition shadow-lg"
          >
            Зарегистрироваться бесплатно
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 mt-16">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-gray-500 text-sm">
          <p>© 2026 Кругослов (krugoslov.ru). Все права защищены.</p>
        </div>
      </div>
    </div>
  );
}
