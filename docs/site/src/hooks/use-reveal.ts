import { useEffect, useState } from "react";

/** Elements the reveal observer watches: single reveals, staggered groups, section rules. */
const REVEAL_SELECTOR = ".ps-rv, .ps-stg, .ps-sec";

/**
 * Run `onFound` for every current and future element matching `selector`.
 * Sections below the fold mount lazily, so a one-time query would miss them.
 */
function watchAll(selector: string, onFound: (el: Element) => void): () => void {
  const seen = new WeakSet<Element>();
  const scan = () => {
    document.querySelectorAll(selector).forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      onFound(el);
    });
  };
  scan();
  const mutations = new MutationObserver(scan);
  mutations.observe(document.body, { childList: true, subtree: true });
  return () => mutations.disconnect();
}

/**
 * Adds `is-in` to reveal elements as they enter the viewport. The CSS that
 * hides them beforehand only applies under `prefers-reduced-motion: no-preference`,
 * so a reduced-motion visitor sees the finished page whether this runs or not.
 */
export function useRevealObserver(): void {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.05, rootMargin: "0px 0px -8% 0px" },
    );
    const stopWatching = watchAll(REVEAL_SELECTOR, (el) => observer.observe(el));
    return () => {
      stopWatching();
      observer.disconnect();
    };
  }, []);
}

/** Id of the section currently filling most of the viewport, for the sticky section nav. */
export function useScrollSpy(enabled: boolean): string {
  const [activeId, setActiveId] = useState("");

  useEffect(() => {
    if (!enabled) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const best = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (best) setActiveId(best.target.id);
      },
      { threshold: [0.2, 0.5], rootMargin: "-48px 0px -45% 0px" },
    );
    const stopWatching = watchAll("main section[id]", (el) => observer.observe(el));
    return () => {
      stopWatching();
      observer.disconnect();
    };
  }, [enabled]);

  return activeId;
}
