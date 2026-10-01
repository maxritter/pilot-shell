import { useSyncExternalStore } from "react";

/** Below this width the page drops what needs a laptop: the clickable Cockpit and the wide diagrams. */
const QUERY = "(max-width: 859px)";

const subscribe = (onChange: () => void) => {
  const media = window.matchMedia(QUERY);
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
};

/** True on phones and narrow windows. Rendering on the server assumes a wide screen. */
export function useNarrow(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => window.matchMedia(QUERY).matches,
    () => false,
  );
}
