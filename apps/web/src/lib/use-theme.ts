import { useCallback, useEffect, useState } from "react";

export type Theme = "light" | "dark";

const STORAGE_KEY = "psb-theme";

function readInitialTheme(): Theme {
  if (typeof document === "undefined") return "light";
  const fromAttr = document.documentElement.dataset.theme;
  return fromAttr === "dark" ? "dark" : "light";
}

/**
 * Тема на уровне документа: data-theme на <html>, сохранение в localStorage.
 * Начальное значение ставит инлайн-скрипт в index.html — без мигания.
 */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(readInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      /* приватный режим — просто не сохраняем */
    }
  }, [theme]);

  const toggle = useCallback(() => {
    setTheme((current) => (current === "light" ? "dark" : "light"));
  }, []);

  return { theme, toggle };
}
