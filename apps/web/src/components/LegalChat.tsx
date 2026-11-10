import { FormEvent, useMemo, useState } from "react";
import {
  askLegal,
  LegalAskResponse,
  LegalCitation,
  LegalHistoryTurn,
} from "@/lib/legal-api";
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

const MAX_CHARS = 4000;

const STARTERS = [
  {
    hint: "Договор аренды",
    q: "Какая арендная плата по договору с ООО «Северный Склад» и до какого числа её нужно вносить?",
  },
  {
    hint: "Трудовой кодекс",
    q: "Какой максимальный срок испытания можно установить главному бухгалтеру?",
  },
  {
    hint: "Если нормы нет",
    q: "Какой размер пособия по беременности и родам?",
  },
];

export function LegalChat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCite, setActiveCite] = useState<string | null>(null);

  const citations = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.role === "assistant" && m.payload.citations?.length) {
        return m.payload.citations;
      }
    }
    return [] as LegalCitation[];
  }, [messages]);

  const overLimit = input.length > MAX_CHARS;
  const askDisabled = busy || !input.trim() || overLimit;

  function historyForAsk(nextUser: string): LegalHistoryTurn[] {
    const turns: LegalHistoryTurn[] = [];
    for (const m of messages) {
      if (m.role === "user") {
        turns.push({ role: "user", content: m.text });
      } else {
        turns.push({ role: "assistant", content: m.payload.answer });
      }
    }
    // API history excludes the current question (sent as `question`)
    void nextUser;
    return turns.slice(-10);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || askDisabled) return;
    setInput("");
    setError(null);
    setActiveCite(null);
    const hist = historyForAsk(q);
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setBusy(true);
    try {
      const payload = await askLegal(q, hist);
      setMessages((prev) => [...prev, { role: "assistant", payload }]);
      if (payload.citations?.[0]) {
        setActiveCite(payload.citations[0].doc_id);
      }
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
                <p className="legal-empty-kicker">База знаний</p>
                <p className="legal-empty-title">
                  Спросите по документам, которые есть в базе
                </p>
                <div className="legal-starters">
                  {STARTERS.map((item, i) => (
                    <button
                      key={item.q}
                      type="button"
                      className={
                        i === 0 ? "legal-starter is-lead" : "legal-starter"
                      }
                      onClick={() => {
                        setInput(item.q);
                        setError(null);
                      }}
                    >
                      <span className="legal-starter-hint">{item.hint}</span>
                      <span className="legal-starter-q">{item.q}</span>
                    </button>
                  ))}
                </div>
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
                  {m.payload.options && m.payload.options.length > 0 && (
                    <ul className="legal-missing">
                      {m.payload.options.map((opt) => (
                        <li key={opt}>{opt}</li>
                      ))}
                    </ul>
                  )}
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
                        <button
                          key={`${c.doc_id}-${i}`}
                          type="button"
                          className={
                            activeCite === c.doc_id
                              ? "legal-cite is-active"
                              : "legal-cite"
                          }
                          onClick={() => setActiveCite(c.doc_id)}
                        >
                          [{i + 1}] {c.span || c.title}
                        </button>
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
              aria-label="Вопрос по нормативным документам"
              aria-invalid={overLimit}
              maxLength={MAX_CHARS + 50}
            />
            <button
              type="submit"
              className="legal-ask"
              aria-disabled={askDisabled}
              disabled={askDisabled}
            >
              {busy ? "Ищем…" : "Спросить"}
            </button>
          </form>
          {overLimit && (
            <p className="legal-error">Лимит {MAX_CHARS} символов</p>
          )}
        </section>

        <aside className="legal-aside">
          <h2>Подтверждения</h2>
          {citations.length === 0 ? (
            <p className="legal-aside-empty">
              {messages.some((m) => m.role === "assistant")
                ? "В этом ответе нет цитат: вопрос не про базу или подтверждающих положений не нашлось."
                : "Фрагменты документов появятся после ответа с цитатами"}
            </p>
          ) : (
            citations.map((c, i) => (
              <article
                key={`${c.doc_id}-${i}`}
                id={`cite-${c.doc_id}`}
                className={`legal-frag${activeCite === c.doc_id ? " legal-frag-active" : ""}`}
              >
                <div className="legal-frag-doc">
                  <span className="legal-frag-index">{i + 1}</span>
                  <span className="legal-frag-title">{c.title}</span>
                  {c.span ? <span className="legal-span">{c.span}</span> : null}
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
