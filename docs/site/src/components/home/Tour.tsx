import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CHAPTERS, PARTS, partOf, type Who } from "@/lib/tour";
import CloseUp from "./CloseUps";

/** The header's height; the step bar pins below it. */
const HEADER = 68;
/** Width where the close-up sits beside the chapters; below it every chapter carries its own. */
const WIDE = 1080;

const dot = (who: Who) => (who === "you" ? "sx-you" : who === "ok" ? "sx-ok" : "sx-ag");

const reducedMotion = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
const finished = () => CHAPTERS.map((c) => c.steps);

/**
 * One change followed from request to pull request, then designs, the team and the setup. Each
 * chapter shows one close-up of the QualityLayer App at reading size: the part of the App that
 * chapter is about, playing its moments one per second. On wide screens the chapters scroll on the
 * left while the close-up stays pinned on the right; on tablets and phones each chapter carries
 * its own close-up, which plays as it scrolls into view, and only the step bar pins.
 */
export default function Tour() {
  const [ch, setCh] = useState(0);
  // Each chapter's moment. With reduced motion every close-up shows complete.
  const [steps, setSteps] = useState<number[]>(() => (reducedMotion() ? finished() : CHAPTERS.map(() => 0)));
  const [tries, setTries] = useState(2);
  const [inline, setInline] = useState(false);

  const tourRef = useRef<HTMLElement>(null);
  const stepsRef = useRef<HTMLOListElement>(null);
  const chRef = useRef(0);
  const inlineRef = useRef(false);

  /** Make chapter `i` current. The pinned close-up replays; an inline one carries on, unless asked to start over. */
  const play = useCallback((i: number, again = false) => {
    chRef.current = i;
    setCh(i);
    setTries(2);
    if (reducedMotion()) return;
    if (again || !inlineRef.current) setSteps((s) => s.map((v, k) => (k === i ? 0 : v)));
  }, []);

  // The current close-up's moments advance one per second.
  const step = steps[ch];
  useEffect(() => {
    if (reducedMotion() || step >= CHAPTERS[ch].steps) return;
    const id = setTimeout(() => setSteps((s) => s.map((v, k) => (k === ch ? v + 1 : v))), 1000);
    return () => clearTimeout(id);
  }, [ch, step]);

  const measure = useCallback(() => {
    const next = document.documentElement.clientWidth < WIDE;
    if (next !== inlineRef.current) {
      inlineRef.current = next;
      setInline(next);
    }
  }, []);

  /**
   * The current chapter. Beside the pinned close-up: the chapter nearest a line a little above
   * mid-screen. Inline: the last chapter whose close-up has risen past 70 % of the screen.
   */
  const current = useCallback(() => {
    const tour = tourRef.current;
    if (!tour) return chRef.current;
    const vh = window.innerHeight;
    if (inlineRef.current) {
      let best = 0;
      tour.querySelectorAll(".sx-ch").forEach((el, i) => {
        const shot = el.querySelector(".sx-iwin") ?? el;
        if (shot.getBoundingClientRect().top <= vh * 0.7) best = i;
      });
      return best;
    }
    let best = chRef.current, bd = Infinity;
    tour.querySelectorAll(".sx-chin").forEach((el, i) => {
      const r = el.getBoundingClientRect(), d = Math.abs((r.top + r.bottom) / 2 - vh * 0.4);
      if (d < bd) {
        bd = d;
        best = i;
      }
    });
    return best;
  }, []);

  const frame = useCallback(() => {
    const tour = tourRef.current;
    if (!tour) return;
    const tr = tour.getBoundingClientRect();
    if (tr.bottom < 0 || tr.top > window.innerHeight) return;
    const best = current();
    if (best !== chRef.current) play(best);
  }, [current, play]);

  useLayoutEffect(() => {
    measure();
  }, [measure]);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        frame();
      });
    };
    const onResize = () => {
      measure();
      frame();
    };
    frame();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
    };
  }, [frame, measure]);

  // Keep the current chapter visible in the step bar when it scrolls sideways.
  useEffect(() => {
    const bar = stepsRef.current, cur = bar?.querySelector<HTMLElement>(".sx-step.on");
    if (bar && cur) bar.scrollLeft = cur.offsetLeft - (bar.clientWidth - cur.offsetWidth) / 2;
  }, [ch]);

  const goTo = (i: number) => {
    const tour = tourRef.current;
    const behavior = reducedMotion() ? "auto" : "smooth";
    if (!tour) return;
    if (inlineRef.current) {
      const el = tour.querySelectorAll(".sx-ch")[i];
      if (!el) return;
      const bar = tour.querySelector(".sx-stage") as HTMLElement | null;
      window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - (HEADER + (bar?.offsetHeight ?? 0) + 12), behavior });
      return;
    }
    const el = tour.querySelectorAll(".sx-chin")[i];
    if (!el) return;
    const r = el.getBoundingClientRect();
    window.scrollTo({ top: r.top + window.scrollY - (window.innerHeight * 0.4 - r.height / 2), behavior });
  };

  const part = partOf(ch);
  const retry = () => setTries((n) => Math.min(3, n + 1));

  return (
    <div className="sx-root">
      <section id="tour" ref={tourRef} className={`sx-tour${inline ? " sx-inl" : ""}`} aria-labelledby="tour-h">
        <h2 id="tour-h" className="w7-sr">How one change goes from request to pull request</h2>
        <div className="sx-chs">
          {CHAPTERS.map((x, i) => (
            <div key={x.id} style={{ display: "contents" }}>
              {x.act && (
                <div id={x.act.id} className="sx-act-h">
                  <h2 className="sx-rv">{x.act.title}</h2>
                  <p className="sx-rv">{x.act.text}</p>
                </div>
              )}
              <article id={x.id} className={`sx-ch${i === 0 ? " first" : ""}${i === CHAPTERS.length - 1 ? " last" : ""}${i === ch ? " on" : ""}`}>
                <div className="sx-chin">
                  <h3 className="sx-h3 sx-rv">{x.title}</h3>
                  {inline && (
                    <div className="sx-iwin sx-rvw" role="img" aria-label={`The QualityLayer App: ${x.step}`}>
                      <div aria-hidden="true" className="sx-cuw">
                        <CloseUp id={x.id} step={steps[i]} tries={i === ch ? tries : 2} onRetry={retry} />
                      </div>
                    </div>
                  )}
                  <p className="sx-chp sx-rv">{x.text}</p>
                  <ul className="sx-bul sx-rv">{x.bullets.map((b) => <li key={b}>{b}</li>)}</ul>
                  <button type="button" onClick={() => play(i, true)} className="sx-replay">Play again</button>
                </div>
              </article>
            </div>
          ))}
        </div>

        <div className="sx-stage">
          <div className="sx-sticky">
            {/* The current part's chapters as pills; the other parts fold into one chip each, so the bar always fits. */}
            <ol ref={stepsRef} className="sx-steps" aria-label="Chapters">
              {PARTS.map((p, k) => (
                <li key={p.label} className={`sx-part${k === part ? " cur" : ""}`}>
                  {k > 0 && <span aria-hidden="true" className="sx-ssep" />}
                  {k === part ? (
                    CHAPTERS.slice(p.from, p.to + 1).map((x, j) => {
                      const i = p.from + j;
                      return (
                        <button key={x.id} type="button" onClick={() => goTo(i)} aria-pressed={i === ch} className={`sx-step${i === ch ? " on" : ""}`}>
                          <span aria-hidden="true" className={dot(x.who)} />{x.step}
                        </button>
                      );
                    })
                  ) : (
                    <button type="button" onClick={() => goTo(p.from)} className="sx-step sx-fold">
                      {p.label}<span aria-hidden="true" className="sx-chev" />
                    </button>
                  )}
                </li>
              ))}
            </ol>

            {!inline && (
              <div className="sx-cupin" role="img" aria-label={`The QualityLayer App: ${CHAPTERS[ch].step}`}>
                <div key={CHAPTERS[ch].id} aria-hidden="true" className="sx-cuw sx-cuin">
                  <CloseUp id={CHAPTERS[ch].id} step={step} tries={tries} onRetry={retry} />
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
