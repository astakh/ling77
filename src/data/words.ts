import { Word } from '../types';

export const dictionary: Word[] = [
  // A1
  { id: 'w1', lemma: 'house', pos: 'noun', level: 'A1', translations: ['дом', 'жилище'] },
  { id: 'w2', lemma: 'water', pos: 'noun', level: 'A1', translations: ['вода'] },
  { id: 'w3', lemma: 'food', pos: 'noun', level: 'A1', translations: ['еда', 'пища'] },
  { id: 'w4', lemma: 'book', pos: 'noun', level: 'A1', translations: ['книга'] },
  { id: 'w5', lemma: 'friend', pos: 'noun', level: 'A1', translations: ['друг', 'подруга'] },
  { id: 'w6', lemma: 'school', pos: 'noun', level: 'A1', translations: ['школа'] },
  { id: 'w7', lemma: 'work', pos: 'noun', level: 'A1', translations: ['работа', 'труд'] },
  { id: 'w8', lemma: 'time', pos: 'noun', level: 'A1', translations: ['время'] },
  { id: 'w9', lemma: 'day', pos: 'noun', level: 'A1', translations: ['день'] },
  { id: 'w10', lemma: 'night', pos: 'noun', level: 'A1', translations: ['ночь'] },
  { id: 'w11', lemma: 'big', pos: 'adjective', level: 'A1', translations: ['большой', 'крупный'] },
  { id: 'w12', lemma: 'small', pos: 'adjective', level: 'A1', translations: ['маленький', 'небольшой'] },
  { id: 'w13', lemma: 'good', pos: 'adjective', level: 'A1', translations: ['хороший', 'добрый'] },
  { id: 'w14', lemma: 'bad', pos: 'adjective', level: 'A1', translations: ['плохой'] },
  { id: 'w15', lemma: 'run', pos: 'verb', level: 'A1', translations: ['бежать', 'бегать'] },
  { id: 'w16', lemma: 'eat', pos: 'verb', level: 'A1', translations: ['есть', 'кушать'] },
  { id: 'w17', lemma: 'sleep', pos: 'verb', level: 'A1', translations: ['спать'] },
  { id: 'w18', lemma: 'read', pos: 'verb', level: 'A1', translations: ['читать'] },
  { id: 'w19', lemma: 'write', pos: 'verb', level: 'A1', translations: ['писать'] },
  { id: 'w20', lemma: 'go', pos: 'verb', level: 'A1', translations: ['идти', 'ехать'] },

  // A2
  { id: 'w21', lemma: 'journey', pos: 'noun', level: 'A2', translations: ['путешествие', 'поездка'] },
  { id: 'w22', lemma: 'weather', pos: 'noun', level: 'A2', translations: ['погода'] },
  { id: 'w23', lemma: 'kitchen', pos: 'noun', level: 'A2', translations: ['кухня'] },
  { id: 'w24', lemma: 'garden', pos: 'noun', level: 'A2', translations: ['сад'] },
  { id: 'w25', lemma: 'bridge', pos: 'noun', level: 'A2', translations: ['мост'] },
  { id: 'w26', lemma: 'quiet', pos: 'adjective', level: 'A2', translations: ['тихий', 'спокойный'] },
  { id: 'w27', lemma: 'bright', pos: 'adjective', level: 'A2', translations: ['яркий', 'светлый'] },
  { id: 'w28', lemma: 'narrow', pos: 'adjective', level: 'A2', translations: ['узкий'] },
  { id: 'w29', lemma: 'arrive', pos: 'verb', level: 'A2', translations: ['прибывать', 'приезжать'] },
  { id: 'w30', lemma: 'discover', pos: 'verb', level: 'A2', translations: ['открывать', 'обнаруживать'] },
  { id: 'w31', lemma: 'remember', pos: 'verb', level: 'A2', translations: ['помнить', 'вспоминать'] },
  { id: 'w32', lemma: 'promise', pos: 'verb', level: 'A2', translations: ['обещать'] },
  { id: 'w33', lemma: 'borrow', pos: 'verb', level: 'A2', translations: ['одалживать', 'занимать'] },
  { id: 'w34', lemma: 'suggest', pos: 'verb', level: 'A2', translations: ['предлагать'] },
  { id: 'w35', lemma: 'comfortable', pos: 'adjective', level: 'A2', translations: ['удобный', 'комфортный'] },
  { id: 'w36', lemma: 'dangerous', pos: 'adjective', level: 'A2', translations: ['опасный'] },
  { id: 'w37', lemma: 'ancient', pos: 'adjective', level: 'A2', translations: ['древний', 'старинный'] },
  { id: 'w38', lemma: 'village', pos: 'noun', level: 'A2', translations: ['деревня', 'село'] },
  { id: 'w39', lemma: 'market', pos: 'noun', level: 'A2', translations: ['рынок', 'маркет'] },
  { id: 'w40', lemma: 'forest', pos: 'noun', level: 'A2', translations: ['лес'] },

  // B1
  { id: 'w41', lemma: 'achievement', pos: 'noun', level: 'B1', translations: ['достижение'] },
  { id: 'w42', lemma: 'opportunity', pos: 'noun', level: 'B1', translations: ['возможность'] },
  { id: 'w43', lemma: 'environment', pos: 'noun', level: 'B1', translations: ['окружение', 'среда'] },
  { id: 'w44', lemma: 'responsibility', pos: 'noun', level: 'B1', translations: ['ответственность'] },
  { id: 'w45', lemma: 'influence', pos: 'noun', level: 'B1', translations: ['влияние'] },
  { id: 'w46', lemma: 'negotiate', pos: 'verb', level: 'B1', translations: ['вести переговоры'] },
  { id: 'w47', lemma: 'persuade', pos: 'verb', level: 'B1', translations: ['убеждать'] },
  { id: 'w48', lemma: 'investigate', pos: 'verb', level: 'B1', translations: ['расследовать', 'исследовать'] },
  { id: 'w49', lemma: 'consider', pos: 'verb', level: 'B1', translations: ['рассматривать', 'обдумывать'] },
  { id: 'w50', lemma: 'remarkable', pos: 'adjective', level: 'B1', translations: ['замечательный', 'необычный'] },
  { id: 'w51', lemma: 'significant', pos: 'adjective', level: 'B1', translations: ['значительный', 'важный'] },
  { id: 'w52', lemma: 'temporary', pos: 'adjective', level: 'B1', translations: ['временный'] },
  { id: 'w53', lemma: 'consequence', pos: 'noun', level: 'B1', translations: ['последствие', 'результат'] },
  { id: 'w54', lemma: 'approach', pos: 'noun', level: 'B1', translations: ['подход', 'приближение'] },
  { id: 'w55', lemma: 'evidence', pos: 'noun', level: 'B1', translations: ['доказательство', 'свидетельство'] },

  // B2
  { id: 'w56', lemma: 'sophisticated', pos: 'adjective', level: 'B2', translations: ['утончённый', 'сложный'] },
  { id: 'w57', lemma: 'controversial', pos: 'adjective', level: 'B2', translations: ['спорный', 'противоречивый'] },
  { id: 'w58', lemma: 'comprehensive', pos: 'adjective', level: 'B2', translations: ['всеобъемлющий', 'комплексный'] },
  { id: 'w59', lemma: 'inevitable', pos: 'adjective', level: 'B2', translations: ['неизбежный'] },
  { id: 'w60', lemma: 'implement', pos: 'verb', level: 'B2', translations: ['внедрять', 'осуществлять'] },
  { id: 'w61', lemma: 'acknowledge', pos: 'verb', level: 'B2', translations: ['признавать'] },
  { id: 'w62', lemma: 'deteriorate', pos: 'verb', level: 'B2', translations: ['ухудшаться'] },
  { id: 'w63', lemma: 'phenomenon', pos: 'noun', level: 'B2', translations: ['явление', 'феномен'] },
  { id: 'w64', lemma: 'dilemma', pos: 'noun', level: 'B2', translations: ['дилемма'] },
  { id: 'w65', lemma: 'breakthrough', pos: 'noun', level: 'B2', translations: ['прорыв'] },
];

export function getWordsByLevel(level: string): Word[] {
  return dictionary.filter(w => w.level === level);
}

export function getWordById(id: string): Word | undefined {
  return dictionary.find(w => w.id === id);
}
