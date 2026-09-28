import { Word } from '../types';

export interface SentenceTemplate {
  sentence: string;
  translation: string;
  wordIds: string[];
}

// Генерируем предложения для каждого слова
export const sentenceTemplates: SentenceTemplate[] = [
  // A1
  { sentence: 'The house on the hill is very old.', translation: 'Дом на холме очень старый.', wordIds: ['w1'] },
  { sentence: 'She drank a glass of water after running.', translation: 'Она выпила стакан воды после бега.', wordIds: ['w2'] },
  { sentence: 'The food at this restaurant is delicious.', translation: 'Еда в этом ресторане вкусная.', wordIds: ['w3'] },
  { sentence: 'I read a book about ancient history.', translation: 'Я прочитал книгу о древней истории.', wordIds: ['w4'] },
  { sentence: 'My best friend lives in another city.', translation: 'Мой лучший друг живёт в другом городе.', wordIds: ['w5'] },
  { sentence: 'The children walk to school every morning.', translation: 'Дети ходят в школу каждое утро.', wordIds: ['w6'] },
  { sentence: 'She found a new job at the hospital.', translation: 'Она нашла новую работу в больнице.', wordIds: ['w7'] },
  { sentence: 'We don\'t have enough time to finish.', translation: 'У нас недостаточно времени, чтобы закончить.', wordIds: ['w8'] },
  { sentence: 'It was a beautiful day for a walk.', translation: 'Это был прекрасный день для прогулки.', wordIds: ['w9'] },
  { sentence: 'The stars shine brightly at night.', translation: 'Звёзды ярко светят ночью.', wordIds: ['w10'] },
  { sentence: 'They live in a big house near the lake.', translation: 'Они живут в большом доме у озера.', wordIds: ['w11'] },
  { sentence: 'The small cat hid under the table.', translation: 'Маленький кот спрятался под столом.', wordIds: ['w12'] },
  { sentence: 'She is a good student at the university.', translation: 'Она хорошая студентка в университете.', wordIds: ['w13'] },
  { sentence: 'The weather was bad so we stayed home.', translation: 'Погода была плохая, поэтому мы остались дома.', wordIds: ['w14'] },
  { sentence: 'The children run fast in the park.', translation: 'Дети быстро бегают в парке.', wordIds: ['w15'] },
  { sentence: 'We eat dinner together every evening.', translation: 'Мы ужинаем вместе каждый вечер.', wordIds: ['w16'] },
  { sentence: 'The baby sleeps through the night.', translation: 'Малыш спит всю ночь.', wordIds: ['w17'] },
  { sentence: 'She likes to read before going to bed.', translation: 'Она любит читать перед сном.', wordIds: ['w18'] },
  { sentence: 'Please write your name on the paper.', translation: 'Пожалуйста, напишите своё имя на бумаге.', wordIds: ['w19'] },
  { sentence: 'We go to the beach every summer.', translation: 'Мы ездим на пляж каждое лето.', wordIds: ['w20'] },

  // A2
  { sentence: 'The journey through the mountains took three days.', translation: 'Путешествие через горы заняло три дня.', wordIds: ['w21'] },
  { sentence: 'The weather changed suddenly during our trip.', translation: 'Погода внезапно изменилась во время нашей поездки.', wordIds: ['w22'] },
  { sentence: 'She prepared a meal in the new kitchen.', translation: 'Она приготовила еду на новой кухне.', wordIds: ['w23'] },
  { sentence: 'The garden is full of colorful flowers.', translation: 'Сад полон красочных цветов.', wordIds: ['w24'] },
  { sentence: 'They crossed the old bridge over the river.', translation: 'Они перешли через старый мост над рекой.', wordIds: ['w25'] },
  { sentence: 'The library is a quiet place to study.', translation: 'Библиотека — тихое место для учёбы.', wordIds: ['w26'] },
  { sentence: 'The bright sun made everyone feel happy.', translation: 'Яркое солнце сделало всех счастливыми.', wordIds: ['w27'] },
  { sentence: 'The narrow path led through the forest.', translation: 'Узкая тропинка вела через лес.', wordIds: ['w28'] },
  { sentence: 'The train will arrive at the station soon.', translation: 'Поезд скоро прибудет на станцию.', wordIds: ['w29'] },
  { sentence: 'Scientists discover new things every day.', translation: 'Учёные открывают новые вещи каждый день.', wordIds: ['w30'] },
  { sentence: 'I remember the first day at school clearly.', translation: 'Я чётко помню первый день в школе.', wordIds: ['w31'] },
  { sentence: 'He promised to help with the project.', translation: 'Он обещал помочь с проектом.', wordIds: ['w32'] },
  { sentence: 'Can I borrow your pen for a moment?', translation: 'Могу я одолжить твою ручку на минуту?', wordIds: ['w33'] },
  { sentence: 'I suggest we take a break now.', translation: 'Я предлагаю нам сделать перерыв сейчас.', wordIds: ['w34'] },
  { sentence: 'This chair is very comfortable to sit in.', translation: 'Этот стул очень удобный.', wordIds: ['w35'] },
  { sentence: 'It is dangerous to swim in this river.', translation: 'Опасно плавать в этой реке.', wordIds: ['w36'] },
  { sentence: 'The ancient castle still stands on the hill.', translation: 'Древний замок всё ещё стоит на холме.', wordIds: ['w37'] },
  { sentence: 'The small village has only one shop.', translation: 'В маленькой деревне только один магазин.', wordIds: ['w38'] },
  { sentence: 'We buy fresh vegetables at the market.', translation: 'Мы покупаем свежие овощи на рынке.', wordIds: ['w39'] },
  { sentence: 'The forest is home to many animals.', translation: 'Лес — дом для многих животных.', wordIds: ['w40'] },

  // B1
  { sentence: 'Her greatest achievement was winning the competition.', translation: 'Её greatest достижение — победа в соревновании.', wordIds: ['w41'] },
  { sentence: 'This job offers a great opportunity for growth.', translation: 'Эта работа предлагает отличную возможность для роста.', wordIds: ['w42'] },
  { sentence: 'We must protect the natural environment.', translation: 'Мы должны защищать природную среду.', wordIds: ['w43'] },
  { sentence: 'Parents have a responsibility to guide their children.', translation: 'Родители несут ответственность за руководство своими детьми.', wordIds: ['w44'] },
  { sentence: 'Social media has a strong influence on young people.', translation: 'Социальные сети оказывают сильное влияние на молодёжь.', wordIds: ['w45'] },
  { sentence: 'They need to negotiate the terms of the contract.', translation: 'Им нужно провести переговоры об условиях контракта.', wordIds: ['w46'] },
  { sentence: 'She tried to persuade him to change his mind.', translation: 'Она пыталась убедить его передумать.', wordIds: ['w47'] },
  { sentence: 'Police investigate the cause of the accident.', translation: 'Полиция расследует причину аварии.', wordIds: ['w48'] },
  { sentence: 'We must consider all options before deciding.', translation: 'Мы должны рассмотреть все варианты перед решением.', wordIds: ['w49'] },
  { sentence: 'She made a remarkable progress in learning English.', translation: 'Она достигла замечательного прогресса в изучении английского.', wordIds: ['w50'] },
  { sentence: 'This is a significant step towards improvement.', translation: 'Это значительный шаг к улучшению.', wordIds: ['w51'] },
  { sentence: 'The temporary solution worked for now.', translation: 'Временное решение пока сработало.', wordIds: ['w52'] },
  { sentence: 'Every action has its consequences.', translation: 'Каждое действие имеет свои последствия.', wordIds: ['w53'] },
  { sentence: 'We need a new approach to solve this problem.', translation: 'Нам нужен новый подход для решения этой проблемы.', wordIds: ['w54'] },
  { sentence: 'There is strong evidence to support this theory.', translation: 'Есть сильные доказательства в поддержку этой теории.', wordIds: ['w55'] },

  // B2
  { sentence: 'The sophisticated system requires careful handling.', translation: 'Сложная система требует осторожного обращения.', wordIds: ['w56'] },
  { sentence: 'The controversial decision sparked heated debate.', translation: 'Спорное решение вызвало жаркие дебаты.', wordIds: ['w57'] },
  { sentence: 'The report provides a comprehensive analysis.', translation: 'Отчёт предоставляет всеобъемлющий анализ.', wordIds: ['w58'] },
  { sentence: 'Change is inevitable in any growing organization.', translation: 'Перемены неизбежны в любой растущей организации.', wordIds: ['w59'] },
  { sentence: 'The government plans to implement new policies.', translation: 'Правительство планирует внедрить новые политики.', wordIds: ['w60'] },
  { sentence: 'She acknowledged her mistake publicly.', translation: 'Она публично признала свою ошибку.', wordIds: ['w61'] },
  { sentence: 'His health began to deteriorate rapidly.', translation: 'Его здоровье начало быстро ухудшаться.', wordIds: ['w62'] },
  { sentence: 'The northern lights are a remarkable phenomenon.', translation: 'Северное сияние — замечательное явление.', wordIds: ['w63'] },
  { sentence: 'She faced a difficult dilemma at work.', translation: 'Она столкнулась с трудной дилеммой на работе.', wordIds: ['w64'] },
  { sentence: 'The discovery was a major breakthrough in medicine.', translation: 'Открытие стало крупным прорывом в медицине.', wordIds: ['w65'] },
];

export function getSentenceForWord(word: Word): SentenceTemplate {
  const templates = sentenceTemplates.filter(t => t.wordIds.includes(word.id));
  if (templates.length > 0) {
    return templates[Math.floor(Math.random() * templates.length)];
  }
  // Fallback
  return {
    sentence: `She uses the word "${word.lemma}" correctly in this sentence.`,
    translation: `Она правильно использует слово "${word.translations[0]}" в этом предложении.`,
    wordIds: [word.id]
  };
}
