const API_URL = (process.env.NEXT_PUBLIC_LEGAL_API_URL || "http://localhost:8090").replace(
  /\/$/,
  "",
);

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
};

export async function askLegal(question: string): Promise<LegalAskResponse> {
  const res = await fetch(`${API_URL}/api/v1/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body.slice(0, 200) || `HTTP ${res.status}`);
  }
  return res.json() as Promise<LegalAskResponse>;
}
