export type LegalCitation = {
  doc_id: string;
  title: string;
  span: string;
  quote: string;
};

export type LegalAskResponse = {
  status: "grounded" | "limited" | "abstain" | "clarify" | "refuse_role" | string;
  answer: string;
  citations: LegalCitation[];
  missing: string[];
  options?: string[];
};

export type LegalHistoryTurn = {
  role: "user" | "assistant";
  content: string;
};

export async function askLegal(
  question: string,
  history: LegalHistoryTurn[] = [],
): Promise<LegalAskResponse> {
  const res = await fetch("/api/v1/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      history: history.slice(-10),
    }),
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    if (res.status === 422) {
      throw new Error("Сервис не принял вопрос: проверьте длину и формулировку.");
    }
    throw new Error(
      body.slice(0, 180) || `Сервис вернул ошибку ${res.status}.`,
    );
  }
  return res.json() as Promise<LegalAskResponse>;
}
