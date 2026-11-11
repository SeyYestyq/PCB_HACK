import { useEffect, useRef, useState } from "react";
import { Check, Clock3, Copy, Info } from "lucide-react";
import type { LegalAskResponse } from "@/lib/legal-api";
import { formatDuration, plural, splitAnswer } from "@/lib/answer-format";
import { verdictFor } from "@/lib/verdicts";

type Props = {
  payload: LegalAskResponse;
  elapsedMs: number | null;
  activeCitation: number | null;
  isLatest: boolean;
  onActivate: (citeIndex: number | null) => void;
  onPickOption: (option: string) => void;
};

/**
 * Карточка ответа: вердикт, проходы-цитаты, блоки «чего не хватило»,
 * счётчики и копирование. Текст ответа не переписывается — только
 * режется по маркерам ядра.
 */
export function AnswerCard({
  payload,
  elapsedMs,
  activeCitation,
  isLatest,
  onActivate,
  onPickOption,
}: Props) {
  const [copied, setCopied] = useState(false);
  const passageRefs = useRef<Record<number, HTMLDivElement | null>>({});

  const verdict = verdictFor(payload);
  const { lead, passages, closing } = splitAnswer(
    payload.answer,
    payload.citations ?? [],
  );
  const documents = new Set((payload.citations ?? []).map((c) => c.doc_id));
  const citeCount = payload.citations?.length ?? 0;
  const showLead =
    lead.length > 0 &&
    !(payload.status === "abstain" && /не найдено подтверждающих/i.test(lead));

  useEffect(() => {
    if (!isLatest || activeCitation === null) return;
    passageRefs.current[activeCitation]?.scrollIntoView({
      block: "nearest",
      behavior: "smooth",
    });
  }, [activeCitation, isLatest]);

  async function copyAnswer() {
    const text = [
      payload.answer,
      ...(payload.citations ?? []).map(
        (c, i) => `[${i + 1}] ${c.title}${c.span ? `, ${c.span}` : ""} — ${c.quote}`,
      ),
    ].join("\n\n");

    if (await writeToClipboard(text)) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } else {
      setCopied(false);
    }
  }

  return (
    <article className={`answer-card tone-${verdict.tone}`} aria-label="Ответ ассистента">
      <div className="answer-head">
        <span className={`stamp stamp-${verdict.tone}`}>
          <span className="stamp-dot" aria-hidden />
          {verdict.label}
        </span>
        {verdict.note ? <span className="answer-note">{verdict.note}</span> : null}
        {elapsedMs !== null && (
          <span className="answer-time">
            <Clock3 size={12} strokeWidth={1.7} aria-hidden />
            {formatDuration(elapsedMs)}
          </span>
        )}
      </div>

      <div className="answer-body">
        {showLead ? <p className="answer-lead">{lead}</p> : null}

        {passages.map((p, index) => {
          const isActive =
            isLatest && p.citeIndex !== null && p.citeIndex === activeCitation;
          const showDoc = index === 0 || passages[index - 1].doc !== p.doc;
          return (
            <div
              key={p.key}
              ref={(el) => {
                if (p.citeIndex !== null) passageRefs.current[p.citeIndex] = el;
              }}
              className={`passage${isActive ? " is-active" : ""}`}
              role={p.citeIndex !== null ? "button" : undefined}
              tabIndex={p.citeIndex !== null ? 0 : undefined}
              aria-label={
                p.citeIndex !== null
                  ? `Фрагмент ${p.citeIndex}, ${p.doc ?? ""}`
                  : undefined
              }
              onClick={() => onActivate(p.citeIndex)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onActivate(p.citeIndex);
                }
              }}
            >
              <div className="passage-head">
                <span className="passage-num">{p.citeIndex ?? "·"}</span>
                {showDoc ? (
                  <span className="passage-doc">{shortDoc(p.doc)}</span>
                ) : null}
                {p.span ? <span className="passage-span">{p.span}</span> : null}
              </div>
              <p className="passage-text">{p.text}</p>
            </div>
          );
        })}

        {closing ? <p className="answer-note answer-note-foot">{closing}</p> : null}

        {payload.status === "abstain" && payload.missing?.length > 0 && (
          <div className="notice">
            <p className="notice-title">
              <Info size={13} strokeWidth={1.8} aria-hidden />
              Чего не хватило для ответа
            </p>
            <ul>
              {payload.missing.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <p className="notice-hint">
              Назовите документ, пункт или реквизит — ассистент ответит только по
              найденным положениям и не будет достраивать норму.
            </p>
          </div>
        )}

        {payload.status === "clarify" && (payload.options?.length ?? 0) > 0 && (
          <div className="notice notice-neutral">
            <p className="notice-title">Уточните, что нужно найти</p>
            <ul>
              {payload.options?.map((option) => (
                <li key={option}>
                  <button
                    type="button"
                    className="option-button"
                    onClick={() => onPickOption(option)}
                  >
                    {option}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {payload.status === "refuse_role" && (
          <div className="notice notice-neutral">
            <p className="notice-title">Что ассистент делает вместо этого</p>
            <p>
              Ищет положения в договорах, локальных регламентах и нормативных
              актах базы знаний и показывает пункты-основания.
            </p>
          </div>
        )}
      </div>

      <div className="answer-foot">
        {citeCount > 0 && (
          <span className="stat">
            <b>{citeCount}</b> {plural(citeCount, "цитата", "цитаты", "цитат")}
          </span>
        )}
        {documents.size > 0 && (
          <span className="stat">
            <b>{documents.size}</b>{" "}
            {plural(documents.size, "документ", "документа", "документов")}
          </span>
        )}
        {citeCount === 0 && <span className="stat">без цитат</span>}
        <button type="button" className="copy-btn" onClick={copyAnswer}>
          {copied ? (
            <Check size={13} strokeWidth={2} aria-hidden />
          ) : (
            <Copy size={13} strokeWidth={1.7} aria-hidden />
          )}
          {copied ? "Скопировано" : "Скопировать"}
          <span className="visually-hidden" role="status">
            {copied ? "Ответ и цитаты скопированы" : ""}
          </span>
        </button>
      </div>
    </article>
  );
}

/**
 * Буфер обмена доступен не всегда (Safari в приватном окне, http-origin).
 * Пробуем Clipboard API, затем скрытую textarea и execCommand.
 */
async function writeToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* падаем в запасной путь */
  }
  try {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(area);
    return ok;
  } catch {
    return false;
  }
}

function shortDoc(doc: string | null): string {
  if (!doc) return "Фрагмент";
  return doc
    .replace(/^документы компании — /, "")
    .replace(/^законы — /, "");
}
