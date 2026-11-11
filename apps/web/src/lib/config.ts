/** Единственный источник продуктовых ограничений и типов сессии. */
export const MAX_QUESTION_CHARS = 4000;

/** Показываем счётчик заранее, чтобы лимит не был сюрпризом. */
export const COUNTER_VISIBLE_FROM = Math.round(MAX_QUESTION_CHARS * 0.75);

export type SessionStats = {
  questions: number;
  citations: number;
  averageMs: number | null;
};
