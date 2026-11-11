import { useRef } from "react";
import { ArrowUp, Loader2 } from "lucide-react";
import { COMPOSER_PLACEHOLDER, TRUST_SHORT } from "@/lib/brand";
import { COUNTER_VISIBLE_FROM, MAX_QUESTION_CHARS } from "@/lib/config";

type Props = {
  value: string;
  busy: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  textareaRef?: React.RefObject<HTMLTextAreaElement | null>;
};

/** Поле вопроса: автовысота, Enter — отправить, Shift+Enter — перенос.
 *  Состояния: default / focus / filled / near-limit / over-limit / loading. */
export function Composer({ value, busy, onChange, onSubmit, textareaRef }: Props) {
  const fallbackRef = useRef<HTMLTextAreaElement>(null);
  const inputRef = textareaRef ?? fallbackRef;

  const overLimit = value.length > MAX_QUESTION_CHARS;
  const showCounter = value.length >= COUNTER_VISIBLE_FROM;
  const canSend = !busy && value.trim().length > 0 && !overLimit;

  const hint = overLimit
    ? `Слишком длинный вопрос: ${value.length} из ${MAX_QUESTION_CHARS} символов`
    : showCounter
      ? `${value.length} / ${MAX_QUESTION_CHARS}`
      : "Только документы базы знаний";

  return (
    <div className="composer-wrap">
      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault();
          if (canSend) onSubmit();
        }}
      >
        <div
          className={`composer-field${overLimit ? " has-error" : ""}`}
          aria-describedby="composer-help"
        >
          <textarea
            ref={inputRef}
            rows={1}
            value={value}
            placeholder={COMPOSER_PLACEHOLDER}
            aria-label={COMPOSER_PLACEHOLDER}
            aria-invalid={overLimit}
            maxLength={MAX_QUESTION_CHARS + 200}
            onChange={(event) => {
              onChange(event.target.value);
              const el = event.currentTarget;
              el.style.height = "auto";
              el.style.height = `${Math.min(el.scrollHeight, 168)}px`;
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                if (canSend) onSubmit();
              }
            }}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!canSend}
            aria-label={busy ? "Ищу ответ" : "Отправить вопрос"}
            aria-busy={busy}
          >
            {busy ? (
              <Loader2 className="btn-spinner" size={17} strokeWidth={2.2} aria-hidden />
            ) : (
              <ArrowUp size={17} strokeWidth={2.2} aria-hidden />
            )}
            <span>{busy ? "Ищу" : "Спросить"}</span>
          </button>
        </div>

        <div className="composer-hint" id="composer-help">
          <span>
            <kbd>Enter</kbd> — отправить, <kbd>Shift</kbd> + <kbd>Enter</kbd> — перенос
          </span>
          <span
            className={overLimit ? "counter-over" : showCounter ? "counter-near" : undefined}
            title={TRUST_SHORT}
            role={overLimit ? "alert" : undefined}
          >
            {hint}
          </span>
        </div>
      </form>
    </div>
  );
}
