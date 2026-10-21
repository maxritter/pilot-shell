/**
 * The attempt to open the QualityLayer App from the landing page of a Slack message. The page hands
 * the link to the App through a hidden frame; when the App opens, the browser loses the reader's
 * focus or the tab is hidden. If neither happens in time, the page offers the three ways on.
 */

export type AttemptPhase = "opened" | "offer";

/** The two things the attempt listens to: the window's focus and the page's visibility. */
export type AttemptTarget = {
  win: Pick<Window, "addEventListener" | "removeEventListener">;
  doc: Pick<Document, "addEventListener" | "removeEventListener" | "visibilityState">;
};

/** Starts the attempt and says its outcome once: `opened`, or `offer` after `ms`. Returns the function that ends it. */
export function startAttempt({ win, doc, ms, onPhase }: AttemptTarget & { ms: number; onPhase: (phase: AttemptPhase) => void }): () => void {
  const stop = () => {
    clearTimeout(timer);
    win.removeEventListener("blur", opened);
    doc.removeEventListener("visibilitychange", hidden);
  };
  const finish = (phase: AttemptPhase) => {
    stop();
    onPhase(phase);
  };
  const opened = () => finish("opened");
  const hidden = () => {
    if (doc.visibilityState === "hidden") finish("opened");
  };
  const timer = setTimeout(() => finish("offer"), ms);
  win.addEventListener("blur", opened);
  doc.addEventListener("visibilitychange", hidden);
  return stop;
}
