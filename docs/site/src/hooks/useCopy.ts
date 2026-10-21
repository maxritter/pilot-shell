import { useCallback, useEffect, useRef, useState } from "react";

export type CopyState = "idle" | "done" | "error";

/** Copy text to the clipboard and report the outcome for a short while. */
export function useCopy(text: string) {
  const [state, setState] = useState<CopyState>("idle");
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  const copy = useCallback(async () => {
    try {
      if (!navigator.clipboard) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(text);
      setState("done");
    } catch {
      setState("error");
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setState("idle"), 2400);
  }, [text]);

  const label = state === "done" ? "Copied" : state === "error" ? "Retry" : "Copy";
  const status =
    state === "done"
      ? "Install command copied."
      : state === "error"
        ? "Copy unavailable. Select the command and copy it."
        : "";

  return { state, copy, label, status };
}
