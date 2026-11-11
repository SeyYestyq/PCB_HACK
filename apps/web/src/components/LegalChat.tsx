import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { askLegal } from "@/lib/legal-api";
import type { LegalAskResponse, LegalHistoryTurn } from "@/lib/legal-api";
import { MAX_QUESTION_CHARS } from "@/lib/config";
import { verdictFor } from "@/lib/verdicts";
import { Sidebar } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { Intro } from "@/components/Intro";
import { AnswerCard } from "@/components/AnswerCard";
import { EvidenceRail } from "@/components/EvidenceRail";
import { Composer } from "@/components/Composer";
import { NoiseOverlay } from "@/components/NoiseOverlay";
import { useTheme } from "@/lib/use-theme";

type Turn = {
  id: number;
  question: string;
  payload?: LegalAskResponse;
  error?: string;
  elapsedMs?: number;
};

/** История для API: прошлые вопросы и ответы без текущего. */
function toHistory(turns: Turn[]): LegalHistoryTurn[] {
  const history: LegalHistoryTurn[] = [];
  for (const turn of turns) {
    history.push({ role: "user", content: turn.question });
    if (turn.payload) {
      history.push({ role: "assistant", content: turn.payload.answer });
    }
  }
  return history;
}

/**
 * Рабочая зона: состояние диалога, отправка и повтор запроса,
 * синхронизация активной цитаты, счётчики сессии и объявления
 * для скринридера.
 */
export function LegalChat() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [activeCitation, setActiveCitation] = useState<number | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const { theme, toggle: toggleTheme } = useTheme();

  const threadRef = useRef<HTMLDivElement>(null);
  const lastTurnRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const nextId = useRef(1);

  const lastAnswerId = useMemo(() => {
    for (let i = turns.length - 1; i >= 0; i -= 1) {
      if (turns[i].payload) return turns[i].id;
    }
    return null;
  }, [turns]);

  const citations = useMemo(() => {
    const answer = turns.find((turn) => turn.id === lastAnswerId);
    return answer?.payload?.citations ?? [];
  }, [turns, lastAnswerId]);

  const stats = useMemo(() => {
    const answered = turns.filter((turn) => turn.payload);
    const citationsTotal = answered.reduce(
      (sum, turn) => sum + (turn.payload?.citations?.length ?? 0),
      0,
    );
    const times = answered
      .map((turn) => turn.elapsedMs)
      .filter((ms): ms is number => typeof ms === "number");
    return {
      questions: turns.length,
      citations: citationsTotal,
      averageMs: times.length
        ? times.reduce((sum, ms) => sum + ms, 0) / times.length
        : null,
    };
  }, [turns]);

  /* Во время поиска — к концу ленты, после ответа — к его началу. */
  useEffect(() => {
    const last = turns[turns.length - 1];
    if (!last) return;
    if (!last.payload) {
      if (window.matchMedia("(max-width: 900px)").matches) {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
      } else {
        const el = threadRef.current;
        el?.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
      }
      return;
    }
    lastTurnRef.current?.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [turns, busy]);

  /* «/» фокусирует поле вопроса, Esc — убирает фокус. */
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const typing =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target?.isContentEditable;

      if (event.key === "/" && !typing) {
        event.preventDefault();
        textareaRef.current?.focus();
      }
      if (event.key === "Escape" && target === textareaRef.current) {
        textareaRef.current?.blur();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const send = useCallback(
    async (raw: string, history: LegalHistoryTurn[]) => {
      const question = raw.trim();
      if (!question || busy) return;

      const id = nextId.current++;
      setTurns((prev) => [...prev, { id, question }]);
      setBusy(true);
      setActiveCitation(null);
      setAnnouncement("Ищу ответ в базе знаний");
      const started = performance.now();

      try {
        const payload = await askLegal(question, history);
        setTurns((prev) =>
          prev.map((turn) =>
            turn.id === id
              ? { ...turn, payload, elapsedMs: performance.now() - started }
              : turn,
          ),
        );
        setActiveCitation(payload.citations?.length ? 1 : null);

        const verdict = verdictFor(payload);
        const count = payload.citations?.length ?? 0;
        setAnnouncement(
          count > 0
            ? `Ответ готов: ${verdict.label.toLowerCase()}, ${count} ${count === 1 ? "цитата" : "цитаты"}.`
            : `Ответ готов: ${verdict.label.toLowerCase()}, без цитат.`,
        );
      } catch (err) {
        const message =
          err instanceof TypeError
            ? "Запрос не дошёл до сервиса ответа. Проверьте подключение и повторите."
            : err instanceof Error && err.message
              ? err.message.slice(0, 240)
              : "Сервис ответа недоступен.";
        setTurns((prev) =>
          prev.map((turn) => (turn.id === id ? { ...turn, error: message } : turn)),
        );
        setAnnouncement("Ответ не получен. Можно повторить запрос.");
      } finally {
        setBusy(false);
      }
    },
    [busy],
  );

  function submitQuestion(question: string, base: Turn[] = turns) {
    void send(question, toHistory(base).slice(-10));
  }

  function submitFromComposer() {
    const question = input.trim();
    if (!question || question.length > MAX_QUESTION_CHARS) return;
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "";
    submitQuestion(question);
  }

  /** Повтор упавшего запроса: тот же вопрос, история без него. */
  function retryTurn(id: number) {
    if (busy) return;
    const index = turns.findIndex((turn) => turn.id === id);
    if (index < 0) return;
    const question = turns[index].question;
    const before = turns.slice(0, index);
    setTurns(before);
    submitQuestion(question, before);
  }

  function useExample(question: string) {
    setInput(question);
    requestAnimationFrame(() => {
      const el = textareaRef.current;
      if (!el) return;
      el.focus();
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 168)}px`;
    });
  }

  function reset() {
    if (busy) return;
    setTurns([]);
    setInput("");
    setActiveCitation(null);
    setAnnouncement("Диалог очищен");
    textareaRef.current?.focus();
  }

  return (
    <div className="shell">
      <div className="backdrop" aria-hidden />
      <NoiseOverlay />

      <Sidebar
        onExample={useExample}
        onReset={reset}
        canReset={turns.length > 0 && !busy}
      />

      <main className="main">
        <Topbar
          onReset={reset}
          canReset={turns.length > 0 && !busy}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        <div className="workspace">
          <div className="chat-col">
            <div className="thread" ref={threadRef}>
              <div className={`thread-inner${turns.length > 0 ? " is-thread" : ""}`}>
                {turns.length === 0 && !busy && <Intro onPick={useExample} />}

                {turns.map((turn, index) => (
                  <div
                    className="turn"
                    key={turn.id}
                    ref={index === turns.length - 1 ? lastTurnRef : undefined}
                  >
                    <div className="turn-user">
                      <p className="user-bubble">{turn.question}</p>
                    </div>

                    {turn.payload ? (
                      <AnswerCard
                        payload={turn.payload}
                        elapsedMs={turn.elapsedMs ?? null}
                        activeCitation={activeCitation}
                        isLatest={turn.id === lastAnswerId}
                        onActivate={setActiveCitation}
                        onPickOption={useExample}
                      />
                    ) : turn.error ? (
                      <div className="error-card" role="alert">
                        <AlertTriangle size={16} strokeWidth={1.8} aria-hidden />
                        <div className="error-card-body">
                          <b>Ответ не получен</b>
                          <p>{turn.error}</p>
                          <button
                            type="button"
                            className="retry-btn"
                            onClick={() => retryTurn(turn.id)}
                            disabled={busy}
                          >
                            <RotateCcw size={13} strokeWidth={1.8} aria-hidden />
                            Повторить
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="loading-card" aria-busy="true">
                        <div className="loading-head">
                          <span className="spinner" aria-hidden />
                          Ищу в базе знаний
                        </div>
                        <div className="loading-lines" aria-hidden>
                          <span className="skeleton-line" />
                          <span className="skeleton-line" />
                          <span className="skeleton-line" />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <Composer
              value={input}
              busy={busy}
              onChange={setInput}
              onSubmit={submitFromComposer}
              textareaRef={textareaRef}
            />
          </div>

          <EvidenceRail
            citations={citations}
            activeIndex={activeCitation}
            onSelect={setActiveCitation}
            hasAnswer={lastAnswerId !== null}
            loading={busy}
            stats={stats}
            onAsk={() => textareaRef.current?.focus()}
          />
        </div>
      </main>

      <p className="visually-hidden" role="status" aria-live="polite">
        {announcement}
      </p>
    </div>
  );
}
