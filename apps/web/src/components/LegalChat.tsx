"use client";

import { FormEvent, useMemo, useState } from "react";
import { askLegal, LegalAskResponse, LegalCitation } from "@/lib/legal-api";
import { DISCLAIMER_SHORT, PRODUCT_NAME } from "@/lib/brand";

type Msg =
  | { role: "user"; text: string }
  | { role: "assistant"; payload: LegalAskResponse };

const STATUS_LABEL: Record<string, string> = {
  grounded: "Подтверждено источниками",
  limited: "Частично подтверждено",
  abstain: "Отказано — данных мало",
  clarify: "Нужно уточнение",
  refuse_role: "Вне компетенции",
};

export function LegalChat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const citations = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.role === "assistant" && m.payload.citations?.length) {
        return m.payload.citations;
      }
    }
    return [] as LegalCitation[];
  }, [messages]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || busy) return;
    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setBusy(true);
    try {
      const payload = await askLegal(q);
      setMessages((prev) => [...prev, { role: "assistant", payload }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка запроса");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="legal-shell">
      <header className="legal-header">
        <span className="legal-mark" aria-hidden />
        <div className="legal-brand">
          <h1>{PRODUCT_NAME}</h1>
          <p>{DISCLAIMER_SHORT}</p>
        </div>
      </header>

      <div className="legal-main">
        <section className="legal-chat" aria-live="polite">
          <div className="legal-thread">
            {messages.length === 0 && (
              <div className="legal-empty">
                <p>Спросите по нормативным документам из базы знаний</p>
                <ul>
                  <li>Какие нормы учесть при проверке правоспособности для кредита?</li>
                  <li>Ставка НДС по старой редакции за 2019 год?</li>
                </ul>
              </div>
            )}
            {messages.map((m, idx) =>
              m.role === "user" ? (
                <div key={idx} className="legal-bubble user">
                  {m.text}
                </div>
              ) : (
                <div
                  key={idx}
                  className={`legal-bubble assistant status-${m.payload.status}`}
                >
                  <div className="legal-meta">
                    {STATUS_LABEL[m.payload.status] ?? m.payload.status}
                  </div>
                  <p>{m.payload.answer}</p>
                  {m.payload.missing?.length > 0 && (
                    <div className="legal-missing-block">
                      <div className="legal-missing-label">Не хватает</div>
                      <ul className="legal-missing">
                        {m.payload.missing.map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {m.payload.citations?.length > 0 && (
                    <div className="legal-inline-cites">
                      {m.payload.citations.map((c, i) => (
                        <a
                          key={c.doc_id}
                          href={`#cite-${c.doc_id}`}
                          className="legal-cite"
                        >
                          [{i + 1}]
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ),
            )}
            {error && <div className="legal-error">{error}</div>}
          </div>

          <form className="legal-composer" onSubmit={onSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Вопрос по нормативным документам"
              disabled={busy}
              aria-label="Вопрос по нормативным документам"
            />
            <button
              type="submit"
              className="legal-ask"
              disabled={busy || !input.trim()}
            >
              {busy ? "…" : "Спросить"}
            </button>
          </form>
        </section>

        <aside className="legal-aside">
          <h2>Подтверждения</h2>
          {citations.length === 0 ? (
            <p className="legal-aside-empty">Фрагменты документов появятся после ответа с цитатами</p>
          ) : (
            citations.map((c, i) => (
              <article key={c.doc_id} id={`cite-${c.doc_id}`} className="legal-frag">
                <div className="legal-frag-doc">
                  [{i + 1}] {c.title}
                  {c.span ? ` · ${c.span}` : ""}
                </div>
                <p>{c.quote}</p>
              </article>
            ))
          )}
        </aside>
      </div>
    </div>
  );
}
