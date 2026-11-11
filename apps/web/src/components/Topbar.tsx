import { Moon, Plus, Sun } from "lucide-react";
import { PRODUCT_NAME, PRODUCT_OWNER } from "@/lib/brand";
import type { Theme } from "@/lib/use-theme";

type Props = {
  onReset: () => void;
  canReset: boolean;
  theme: Theme;
  onToggleTheme: () => void;
};

/**
 * Шапка рабочей зоны: контекст, состояние базы знаний, тема и действие.
 * h1 один на страницу и живёт здесь — видим на мобиле, скрыт
 * визуально на десктопе, где название уже есть в сайдбаре.
 */
export function Topbar({ onReset, canReset, theme, onToggleTheme }: Props) {
  const nextTheme = theme === "light" ? "тёмную" : "светлую";

  return (
    <header className="topbar">
      <h1 className="topbar-title">
        {PRODUCT_NAME}
        <span className="topbar-sub">{PRODUCT_OWNER}</span>
      </h1>

      <p className="topbar-crumb">
        Юридическая служба <span aria-hidden> / </span>
        <b>Ассистент по базе знаний</b>
      </p>

      <div className="topbar-right">
        <span className="pill" title="Поиск ограничен выданной базой знаний">
          <span className="pill-dot" aria-hidden />
          База знаний подключена
        </span>
        <button
          type="button"
          className="theme-toggle"
          onClick={onToggleTheme}
          aria-label={`Включить ${nextTheme} тему`}
          title={`Включить ${nextTheme} тему`}
        >
          {theme === "light" ? (
            <Moon size={16} strokeWidth={1.7} aria-hidden />
          ) : (
            <Sun size={16} strokeWidth={1.7} aria-hidden />
          )}
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={onReset}
          disabled={!canReset}
        >
          <Plus size={15} strokeWidth={2} aria-hidden />
          <span>Новый диалог</span>
        </button>
      </div>
    </header>
  );
}
