import { useMemo, useState } from "react";
import { ChevronDown, FileSearch, Layers, ShieldCheck } from "lucide-react";
import type { LegalCitation } from "@/lib/legal-api";
import { formatDuration, plural } from "@/lib/answer-format";
import type { SessionStats } from "@/lib/config";
import { useCountUp } from "@/lib/use-count-up";

type Props = {
  citations: LegalCitation[];
  activeIndex: number | null;
  onSelect: (index: number) => void;
  hasAnswer: boolean;
  loading: boolean;
  stats: SessionStats;
  onAsk: () => void;
};

type Group = {
  docId: string;
  title: string;
  kind: string;
  items: { citation: LegalCitation; position: number }[];
};

/**
 * Панель источников: фрагменты сгруппированы по документу, чтобы один
 * договор не повторялся в заголовках. Плюс «паспорт сессии» с реальными
 * счётчиками и скелетоны на время поиска.
 */
export function EvidenceRail({
  citations,
  activeIndex,
  onSelect,
  hasAnswer,
  loading,
  stats,
  onAsk,
}: Props) {
  const [open, setOpen] = useState(false);

  const groups = useMemo(() => {
    const map = new Map<string, Group>();
    citations.forEach((citation, index) => {
      const group = map.get(citation.doc_id) ?? {
        docId: citation.doc_id,
        title: cleanTitle(citation.title),
        kind: sourceKind(citation.title),
        items: [],
      };
      group.items.push({ citation, position: index + 1 });
      map.set(citation.doc_id, group);
    });
    return [...map.values()];
  }, [citations]);

  return (
    <aside className={`rail${open ? " is-open" : ""}`} aria-label="Источники ответа">
      <div className="rail-head">
        <h2 className="rail-title">Источники</h2>
        {citations.length > 0 && (
          <span className="rail-count">
            {citations.length}{" "}
            {plural(citations.length, "фрагмент", "фрагмента", "фрагментов")} ·{" "}
            {groups.length} {plural(groups.length, "документ", "документа", "документов")}
          </span>
        )}
        <button
          type="button"
          className="rail-toggle"
          aria-expanded={open}
          aria-label={open ? "Свернуть источники" : "Показать источники"}
          onClick={() => setOpen((value) => !value)}
        >
          <ChevronDown size={16} strokeWidth={1.8} aria-hidden />
        </button>
      </div>

      <div className="rail-inner">
        {stats.questions > 0 && <SessionCard stats={stats} />}

        {loading && <RailSkeleton />}

        {!loading && groups.length === 0 && (
          <div className="rail-empty">
            <span className="rail-empty-icon" aria-hidden>
              <FileSearch size={18} strokeWidth={1.6} />
            </span>
            <p className="rail-empty-title">
              {hasAnswer ? "В ответе нет цитат" : "Фрагменты появятся здесь"}
            </p>
            <p className="rail-empty-text">
              {hasAnswer
                ? "Подтверждающих положений в базе знаний не нашлось, либо вопрос вне нормативной темы."
                : "Ассистент покажет документ, номер пункта и дословную цитату, на которой построен ответ."}
            </p>
            {!hasAnswer && (
              <button type="button" className="rail-empty-cta" onClick={onAsk}>
                Задать вопрос
              </button>
            )}
          </div>
        )}

        {!loading &&
          groups.map((group) => (
            <section className="evidence-group" key={group.docId}>
              <p className="evidence-doc">
                <span className="evidence-doc-title">{group.title}</span>
                <span className="tag">{group.kind}</span>
              </p>
              {group.items.map(({ citation, position }) => (
                <button
                  key={`${citation.doc_id}-${position}`}
                  type="button"
                  className={`evidence-item${activeIndex === position ? " is-active" : ""}`}
                  aria-current={activeIndex === position ? "true" : undefined}
                  onClick={() => onSelect(position)}
                >
                  <span className="evidence-head">
                    <span className="evidence-num">{position}</span>
                    {citation.span ? (
                      <span className="tag tag-blue">{citation.span}</span>
                    ) : null}
                  </span>
                  <span className="evidence-quote">{citation.quote}</span>
                </button>
              ))}
            </section>
          ))}
      </div>
    </aside>
  );
}

function SessionCard({ stats }: { stats: SessionStats }) {
  const questions = useCountUp(stats.questions);
  const citations = useCountUp(stats.citations);
  const average = useCountUp(stats.averageMs ?? 0);

  return (
    <div className="session-card grain-surface">
      <p className="session-label">
        <Layers size={12} strokeWidth={1.8} aria-hidden />
        Паспорт сессии
      </p>
      <div className="session-metrics">
        <div>
          <span className="metric-value">{questions}</span>
          <span className="metric-label">
            {plural(stats.questions, "вопрос", "вопроса", "вопросов")}
          </span>
        </div>
        <div>
          <span className="metric-value">{citations}</span>
          <span className="metric-label">
            {plural(stats.citations, "цитата", "цитаты", "цитат")}
          </span>
        </div>
        <div>
          <span className="metric-value">
            {stats.averageMs === null ? "—" : formatDuration(average)}
          </span>
          <span className="metric-label">средний ответ</span>
        </div>
      </div>
      <p className="session-foot">
        <ShieldCheck size={12} strokeWidth={1.8} aria-hidden />
        Внешние источники не используются
      </p>
    </div>
  );
}

/** Пока идёт поиск, вместо пустоты показываем форму будущих карточек. */
function RailSkeleton() {
  return (
    <div className="rail-skeleton" aria-hidden>
      <div className="rail-skeleton-card">
        <span className="skeleton-line" style={{ width: "62%" }} />
        <span className="skeleton-line" style={{ width: "34%" }} />
        <span className="skeleton-line" style={{ width: "92%" }} />
        <span className="skeleton-line" style={{ width: "82%" }} />
      </div>
      <div className="rail-skeleton-card">
        <span className="skeleton-line" style={{ width: "48%" }} />
        <span className="skeleton-line" style={{ width: "88%" }} />
      </div>
    </div>
  );
}

function cleanTitle(title: string): string {
  return title
    .replace(/^документы компании — /, "")
    .replace(/^законы — /, "");
}

function sourceKind(title: string): string {
  if (title.startsWith("законы")) return "нормативный акт";
  if (title.startsWith("документы компании")) return "документ компании";
  return "база знаний";
}
