import type { LegalAskResponse } from "@/lib/legal-api";

export type VerdictTone = "ok" | "partial" | "stop";

export type Verdict = {
  label: string;
  note?: string;
  tone: VerdictTone;
};

/** Один словарь вердиктов: карточка ответа, объявления для скринридера. */
export const VERDICTS: Record<string, Verdict> = {
  grounded: { label: "Подтверждено источниками", tone: "ok" },
  limited: { label: "Подтверждено частично", tone: "partial" },
  abstain: {
    label: "Обоснованный отказ",
    note: "подтверждающих положений в базе нет",
    tone: "stop",
  },
  clarify: {
    label: "Нужно уточнение",
    note: "вопрос понят неоднозначно",
    tone: "partial",
  },
  refuse_role: {
    label: "Вне компетенции ассистента",
    note: "вопрос не про нормативную базу",
    tone: "stop",
  },
};

export function verdictFor(payload: LegalAskResponse): Verdict {
  return VERDICTS[payload.status] ?? { label: payload.status, tone: "stop" };
}
