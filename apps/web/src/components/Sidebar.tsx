import { Files, ListChecks, Scale, ShieldCheck, Sparkle } from "lucide-react";
import { PRODUCT_BUILD, PRODUCT_NAME, PRODUCT_OWNER, EXAMPLES } from "@/lib/brand";

const EXAMPLE_ICON = {
  contract: Files,
  labor: Scale,
  absence: ListChecks,
} as const;

type Props = {
  onExample: (question: string) => void;
  onReset: () => void;
  canReset: boolean;
};

/**
 * Тёмный навигационный контур: бренд, действие «новый диалог»,
 * быстрые примеры и напоминание о границах базы знаний.
 * На экранах < 1100px скрывается — действия переезжают в шапку.
 */
export function Sidebar({ onExample, onReset, canReset }: Props) {
  return (
    <nav className="sidebar" aria-label="Диалог с ассистентом">
      <div className="sidebar-brand">
        <span className="brand-mark" aria-hidden>
          §
        </span>
        <div>
          <p className="brand-name">{PRODUCT_NAME}</p>
          <span className="brand-sub">{PRODUCT_OWNER}</span>
        </div>
      </div>

      <div className="sidebar-section">
        <button
          type="button"
          className="sidebar-action"
          onClick={onReset}
          disabled={!canReset}
        >
          <Sparkle size={16} strokeWidth={1.6} aria-hidden />
          Новый диалог
        </button>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-label">Примеры запросов</p>
        <div className="sidebar-list">
          {EXAMPLES.map((example) => {
            const Icon = EXAMPLE_ICON[example.icon];
            return (
              <button
                key={example.question}
                type="button"
                className="sidebar-example"
                onClick={() => onExample(example.question)}
              >
                <Icon size={14} strokeWidth={1.6} aria-hidden />
                <span>{example.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="sidebar-foot">
        <div className="trust-card">
          <ShieldCheck size={15} strokeWidth={1.6} aria-hidden />
          <p>
            Ответы только по документам базы знаний. Нет положения — отказ с
            указанием, чего не хватило.
          </p>
        </div>
        <p className="sidebar-version">{PRODUCT_BUILD}</p>
      </div>
    </nav>
  );
}
