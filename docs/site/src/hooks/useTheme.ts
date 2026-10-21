import { useCallback, useSyncExternalStore } from "react";

export type Theme = "light" | "dark";

/** The same key and values as the docs (Docusaurus), which share this origin, so both keep one choice. */
const KEY = "theme";
const DARK = "(prefers-color-scheme: dark)";
const listeners = new Set<() => void>();

function saved(): Theme | null {
  try {
    const value = localStorage.getItem(KEY);
    return value === "light" || value === "dark" ? value : null;
  } catch {
    return null;
  }
}

function current(): Theme {
  return saved() ?? (window.matchMedia(DARK).matches ? "dark" : "light");
}

/** Until the first click the system decides; from then on the last choice holds. */
export function applySavedTheme(): void {
  const theme = saved();
  if (theme) document.documentElement.dataset.theme = theme;
}

const subscribe = (onChange: () => void) => {
  listeners.add(onChange);
  const media = window.matchMedia(DARK);
  media.addEventListener("change", onChange);
  window.addEventListener("storage", onChange);
  return () => {
    listeners.delete(onChange);
    media.removeEventListener("change", onChange);
    window.removeEventListener("storage", onChange);
  };
};

export function useTheme(): { theme: Theme; toggle: () => void } {
  const theme = useSyncExternalStore(subscribe, current, () => "dark" as Theme);
  const toggle = useCallback(() => {
    const next: Theme = current() === "dark" ? "light" : "dark";
    try {
      localStorage.setItem(KEY, next);
    } catch {
      // The choice then lasts for this page only.
    }
    document.documentElement.dataset.theme = next;
    for (const listener of listeners) listener();
  }, []);
  return { theme, toggle };
}
