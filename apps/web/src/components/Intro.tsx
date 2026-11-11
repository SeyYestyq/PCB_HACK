import {
  ArrowUpRight,
  FileSignature,
  Layers,
  Scale,
  SearchX,
  ShieldCheck,
} from "lucide-react";
import { EXAMPLES, HERO_CHIPS, HERO_LABEL, HERO_TEXT } from "@/lib/brand";

const EXAMPLE_ICON = {
  contract: FileSignature,
  labor: Scale,
  absence: SearchX,
} as const;

const CHIP_ICONS = [Layers, ShieldCheck, SearchX] as const;

const STEPS = [
  { title: "Вопрос", text: "Формулируете запрос по документам банка" },
  { title: "Поиск", text: "Ассистент ищет только в выданной базе знаний" },
  { title: "Основание", text: "Получаете пункт и дословную цитату" },
];

/** Первый экран: что делает продукт, как он проверяет ответ и с чего начать. */
export function Intro({ onPick }: { onPick: (question: string) => void }) {
  return (
    <section aria-label="Начало работы">
      <div className="hero grain-surface">
        <span className="hero-grid" aria-hidden />
        <span className="hero-sheen" aria-hidden />

        <div className="hero-copy">
          <p className="hero-label">{HERO_LABEL}</p>
          <h2 className="hero-title">Ответ по документам — с пунктом-основанием</h2>
          <p className="hero-text">{HERO_TEXT}</p>
        </div>

        <div className="hero-chips">
          {HERO_CHIPS.map((chip, index) => {
            const Icon = CHIP_ICONS[index] ?? Layers;
            return (
              <span className="hero-chip" key={chip}>
                <Icon size={13} strokeWidth={1.7} aria-hidden />
                {chip}
              </span>
            );
          })}
        </div>

        <div className="hero-aside" aria-hidden>
          <div className="hero-doc">
            <p className="hero-doc-head">
              Ответ <span>п. 3.1</span>
            </p>
            <span className="hero-doc-line w1" />
            <span className="hero-doc-line w2" />
            <span className="hero-doc-line w3" />
            <span className="hero-doc-quote">цитата из документа</span>
          </div>
        </div>
      </div>

      <p className="section-label section-label-spaced">
        С чего начать
        <span className="section-label-note">три сценария, включая отказ</span>
      </p>

      <div className="starters">
        {EXAMPLES.map((example, index) => {
          const Icon = EXAMPLE_ICON[example.icon];
          return (
            <button
              key={example.question}
              type="button"
              className="starter"
              style={{ animationDelay: `${60 + index * 60}ms` }}
              onClick={() => onPick(example.question)}
            >
              <ArrowUpRight
                className="starter-arrow"
                size={16}
                strokeWidth={1.6}
                aria-hidden
              />
              <span className="starter-icon">
                <Icon size={16} strokeWidth={1.7} aria-hidden />
              </span>
              <span className="starter-label">{example.label}</span>
              <span className="starter-q">{example.question}</span>
            </button>
          );
        })}
      </div>

      <ol className="steps">
        {STEPS.map((step, index) => (
          <li className="step" key={step.title}>
            <span className="step-num" aria-hidden>
              {index + 1}
            </span>
            <div>
              <b>{step.title}</b>
              <p>{step.text}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
