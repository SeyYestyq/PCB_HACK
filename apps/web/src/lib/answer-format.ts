import type { LegalCitation } from "@/lib/legal-api";

/**
 * Ответ ядра приходит единым текстом, где каждый фрагмент помечен
 * «Согласно <документ> (<пункт>): …». Разбираем его на вводную часть и
 * проходы-цитаты, чтобы читать ответ как заключение со ссылками.
 * Текст не переписывается: только режется по собственным маркерам ядра.
 */

export type Passage = {
  key: string;
  doc: string | null;
  span: string | null;
  text: string;
  citeIndex: number | null;
  citation: LegalCitation | null;
};

const MARK = /Согласно\s+([^():]{3,180}?)\s*\(([^()]{1,64})\):\s*/g;

const CLOSING = /\s*Выводы ограничены найденными фрагментами базы знаний\.?\s*$/i;

export function splitAnswer(
  answer: string,
  citations: LegalCitation[],
): { lead: string; passages: Passage[]; closing: string } {
  const text = answer.trim();
  const closingMatch = text.match(CLOSING);
  const closing = closingMatch ? "Выводы ограничены найденными фрагментами базы знаний." : "";
  const body = closingMatch ? text.slice(0, closingMatch.index).trim() : text;
  const marks: { doc: string; span: string; start: number; bodyStart: number }[] = [];

  MARK.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = MARK.exec(text)) !== null) {
    marks.push({
      doc: m[1].trim(),
      span: m[2].trim(),
      start: m.index,
      bodyStart: m.index + m[0].length,
    });
  }

  if (marks.length === 0) {
    return { lead: body, passages: [], closing };
  }

  const lead = body.slice(0, marks[0].start).trim();
  const used = new Set<string>();
  const passages: Passage[] = marks.map((mark, i) => {
    const end = i + 1 < marks.length ? marks[i + 1].start : body.length;
    const passageText = body.slice(mark.bodyStart, end).trim();
    const hit = citations.find(
      (c, index) =>
        !used.has(`${c.doc_id}-${index}`) &&
        same(c.title, mark.doc) &&
        same(c.span, mark.span),
    );
    const hitIndex = hit ? citations.indexOf(hit) : null;
    if (hit && hitIndex !== null) used.add(`${hit.doc_id}-${hitIndex}`);
    return {
      key: `${mark.doc}-${mark.span}-${i}`,
      doc: mark.doc,
      span: mark.span,
      text: passageText,
      citeIndex: hitIndex === null ? null : hitIndex + 1,
      citation: hit ?? null,
    };
  });

  return { lead, passages, closing };
}

function same(a: string | undefined, b: string): boolean {
  return (a ?? "").trim() === b.trim();
}

export function plural(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${Math.round(ms / 10) * 10} мс`;
  return `${(ms / 1000).toFixed(1).replace(".", ",")} с`;
}
