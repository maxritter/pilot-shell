import { useCallback, useSyncExternalStore } from "react";

/** Below this width the page drops what needs a laptop: the clickable App and the wide diagrams. */
const DEFAULT_MAX_WIDTH = 859;

/** True on phones and narrow windows, up to `maxWidth` pixels. Rendering on the server assumes a wide screen. */
export function useNarrow(maxWidth: number = DEFAULT_MAX_WIDTH): boolean {
  const query = `(max-width: ${maxWidth}px)`;
  const subscribe = useCallback(
    (onChange: () => void) => {
      const media = window.matchMedia(query);
      media.addEventListener("change", onChange);
      return () => media.removeEventListener("change", onChange);
    },
    [query],
  );
  return useSyncExternalStore(
    subscribe,
    () => window.matchMedia(query).matches,
    () => false,
  );
}
