import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CHAPTERS, nextBar, PARTS, partOf, STAGES, type Who } from "@/lib/tour";
import TourScenes from "./TourScenes";

/** The header's height; the window pins below it. */
const HEADER = 68;
/** Widths where the window sits beside the chapters, and below which it gets its narrow phone layout. */
const WIDE = 1080;
const PHONE = 640;

const dot = (who: Who) => (who === "you" ? "sx-you" : who === "ok" ? "sx-ok" : "sx-ag");
const NAV: [string, number][] = [["Tasks", 0], ["Team", 2], ["Settings", 0]];

type Layout = { lw: number; lh: number; sc: number; side: boolean };

const reducedMotion = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/**
 * One change followed from request to pull request, then the team and the setup. The chapters
 * scroll on the left while the App window stays pinned on the right; on tablets and phones the
 * window pins under the header and the chapters scroll beneath it. Each chapter plays a short scene.
 */
export default function Tour() {
  const [ch, setCh] = useState(0);
  // With reduced motion every scene shows complete, the first one too.
  const [step, setStep] = useState(() => (reducedMotion() ? CHAPTERS[0].steps : 0));
  const [tries, setTries] = useState(2);
  const [layout, setLayout] = useState<Layout>({ lw: 940, lh: 600, sc: 0.8, side: true });

  const tourRef = useRef<HTMLElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const dockRef = useRef<HTMLDivElement>(null);
  const stepsRef = useRef<HTMLOListElement>(null);
  const chsRef = useRef<HTMLDivElement>(null);
  const chRef = useRef(0);
  // The scroll handler reads the layout without waiting for a render.
  const layoutRef = useRef(layout);

  const play = useCallback((i: number) => {
    chRef.current = i;
    setCh(i);
    setTries(2);
    setStep(reducedMotion() ? CHAPTERS[i].steps : 0);
  }, []);

  // The scene's parts appear one per second.
  useEffect(() => {
    if (reducedMotion() || step >= CHAPTERS[ch].steps) return;
    const id = setTimeout(() => setStep((s) => s + 1), 1000);
    return () => clearTimeout(id);
  }, [ch, step]);

  // Fit the window to its column: a fixed inner size, scaled. Phones get their own narrow layout.
  const measure = useCallback(() => {
    const stage = stageRef.current;
    if (!stage) return;
    const rw = document.documentElement.clientWidth, vh = window.innerHeight, w = stage.clientWidth;
    let next: Layout;
    if (rw >= WIDE) next = { lw: 940, lh: 600, side: true, sc: Math.min(w / 940, (vh - 96 - HEADER) / 600) };
    else if (rw > PHONE) next = { lw: 940, lh: 600, side: true, sc: Math.min(w / 940, (vh * 0.5) / 600) };
    else next = { lw: 400, lh: 440, side: false, sc: Math.min(w / 400, (vh * 0.46) / 440) };
    next.sc = Math.max(0.3, Math.round(next.sc * 1000) / 1000);
    const cur = layoutRef.current;
    if (cur.lw !== next.lw || cur.lh !== next.lh || cur.sc !== next.sc || cur.side !== next.side) {
      layoutRef.current = next;
      setLayout(next);
    }
  }, []);

  // The reading line: a little above mid-screen beside the window, or mid-way through the space below the pinned window.
  const readLine = useCallback(() => {
    const vh = window.innerHeight, stage = stageRef.current;
    if (!stage || document.documentElement.clientWidth >= WIDE) return vh * 0.4;
    const top = HEADER + stage.offsetHeight;
    return top + (vh - top) / 2;
  }, []);

  // On wide screens the window starts large and centred under the hero, then settles into its column as you scroll.
  const dockFrame = useCallback(() => {
    const tour = tourRef.current, stage = stageRef.current, dock = dockRef.current, bar = stepsRef.current, chs = chsRef.current;
    if (!tour || !stage || !dock) return;
    const y = window.scrollY;
    if (document.documentElement.clientWidth >= WIDE && !reducedMotion()) {
      const tr = tour.getBoundingClientRect(), sr = stage.getBoundingClientRect();
      const end = Math.max(1, tr.top + y - (HEADER + 12));
      const p = Math.min(1, Math.max(0, y / end)), e = p * p * (3 - 2 * p), q = 1 - e;
      const { lw, sc } = layoutRef.current;
      const targetW = Math.min(tr.width - 2 * parseFloat(getComputedStyle(tour).paddingLeft || "0"), 1200);
      const k = Math.max(1, targetW / (lw * sc));
      const tx = tr.left + tr.width / 2 - (sr.left + sr.width / 2), ty = -dock.offsetTop + 8;
      dock.style.transform = q < 0.002 ? "" : `translate(${(tx * q).toFixed(1)}px,${(ty * q).toFixed(1)}px) perspective(2200px) rotateX(${(16 * q).toFixed(2)}deg) scale(${(1 + (k - 1) * q).toFixed(4)})`;
      if (bar) bar.style.opacity = e.toFixed(3);
      if (chs) chs.style.opacity = Math.max(0, (e - 0.6) / 0.4).toFixed(3);
    } else {
      dock.style.transform = "";
      if (bar) bar.style.opacity = "";
      if (chs) chs.style.opacity = "";
    }
  }, []);

  // Per scroll frame: the window's position, then the chapter at the reading line.
  const frame = useCallback(() => {
    dockFrame();
    const tour = tourRef.current;
    if (!tour) return;
    const tr = tour.getBoundingClientRect();
    if (tr.bottom < 0 || tr.top > window.innerHeight) return;
    const line = readLine();
    let best = chRef.current, bd = Infinity;
    tour.querySelectorAll(".sx-chin").forEach((el, i) => {
      const r = el.getBoundingClientRect(), d = Math.abs((r.top + r.bottom) / 2 - line);
      if (d < bd) {
        bd = d;
        best = i;
      }
    });
    if (best !== chRef.current) play(best);
  }, [dockFrame, readLine, play]);

  // Below the pinned window, each chapter takes exactly the space left, so the current one is always in view.
  const fitBelow = useCallback(() => {
    const tour = tourRef.current, stage = stageRef.current;
    if (!tour || !stage) return;
    tour.style.setProperty("--sx-under", `${HEADER + stage.offsetHeight}px`);
    tour.style.setProperty("--sx-below", `${Math.max(240, window.innerHeight - HEADER - stage.offsetHeight)}px`);
  }, []);

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
      fitBelow();
      frame();
    };
    measure();
    frame();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
    };
  }, [frame, measure, fitBelow]);

  // A new scale changes the window's size, so its docked position is measured again.
  useLayoutEffect(() => {
    fitBelow();
    dockFrame();
  }, [layout, fitBelow, dockFrame]);

  // Keep the current chapter visible in the step bar when it scrolls sideways.
  useEffect(() => {
    const bar = stepsRef.current, current = bar?.querySelector<HTMLElement>(".sx-step.on");
    if (bar && current) bar.scrollLeft = current.offsetLeft - (bar.clientWidth - current.offsetWidth) / 2;
  }, [ch]);

  const goTo = (i: number) => {
    const el = tourRef.current?.querySelectorAll(".sx-chin")[i];
    if (!el) return;
    const r = el.getBoundingClientRect();
    window.scrollTo({ top: r.top + window.scrollY - (readLine() - r.height / 2), behavior: reducedMotion() ? "auto" : "smooth" });
  };

  const c = CHAPTERS[ch], w = c.win, nx = nextBar(ch, step), part = partOf(ch);
  const { lw, lh, sc, side } = layout;

  return (
    <div className="sx-root">
      <section id="tour" ref={tourRef} className="sx-tour" aria-labelledby="tour-h">
        <h2 id="tour-h" className="w7-sr">How one change goes from request to pull request</h2>
        <div ref={chsRef} className="sx-chs">
          {CHAPTERS.map((x, i) => (
            <div key={x.id} style={{ display: "contents" }}>
              {x.act && (
                <div id={x.act.id} className="sx-act-h">
                  <h2>{x.act.title}</h2>
                  <p>{x.act.text}</p>
                </div>
              )}
              <article id={x.id} className={`sx-ch${i === 0 ? " first" : ""}${i === CHAPTERS.length - 1 ? " last" : ""}${i === ch ? " on" : ""}`}>
                <div className="sx-chin">
                  <h3 className="sx-h3">{x.title}</h3>
                  <p className="sx-chp">{x.text}</p>
                  <ul className="sx-bul">{x.bullets.map((b) => <li key={b}>{b}</li>)}</ul>
                  <button type="button" onClick={() => play(i)} className="sx-replay">Play again</button>
                </div>
              </article>
            </div>
          ))}
        </div>

        <div ref={stageRef} className="sx-stage">
          <div className="sx-sticky">
            {/* The current part's chapters as pills; the other parts fold into one chip each, so the bar always fits. */}
            <ol ref={stepsRef} className="sx-steps sx-fade" aria-label="Chapters">
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

            <div ref={dockRef} className="sx-dock">
              <div role="region" aria-label={`The QualityLayer App: ${c.title}`} className="sx-win" style={{ width: Math.round(lw * sc) + 2 }}>
                <div className="sx-bar" aria-hidden="true"><i /><i /><i /><span>{w.title}</span></div>
                {/* An illustration of the App; the chapter beside it says the same in words. */}
                <div className="sx-fit" aria-hidden="true" style={{ height: Math.round(lh * sc) }}>
                  <div className={`sx-scale${side ? "" : " sx-nw"}`} style={{ width: lw, height: lh, transform: `scale(${sc})` }}>
                    {side && (
                      <aside className="sx-side">
                        <p className="sx-sbrand"><span aria-hidden="true" className="sx-mark" />QualityLayer</p>
                        {NAV.map(([label, badge], k) => (
                          <span key={label} className={`sx-navi${k === w.nav ? " on" : ""}`}>{label}{badge > 0 && <b>{badge}</b>}</span>
                        ))}
                        <p className="sx-sg">{w.head}</p>
                        {w.side.map((t) => (
                          <div key={t.name} className={`sx-ti${t.on ? " on" : ""}`}>
                            <span aria-hidden="true" className={dot(t.who)} />
                            <span className="sx-tin"><b>{t.name}</b><small>{t.sub}</small></span>
                          </div>
                        ))}
                      </aside>
                    )}
                    <div className="sx-main">
                      <div className="sx-mh">
                        <div style={{ minWidth: 0 }}>
                          <p className="sx-mt">{w.doc}</p>
                          {w.stage >= 0 && (
                            <ol className="sx-stg" aria-label="Steps of this task">
                              {STAGES.map((label, k) => (
                                <li key={label} className={`sx-sp${k < w.stage ? " done" : k === w.stage ? ` cur${w.chip[0] === "ag" ? " ag" : ""}` : ""}`}>
                                  {k < w.stage ? "✓ " : ""}{label}
                                </li>
                              ))}
                            </ol>
                          )}
                        </div>
                        <span className={`sx-chip ${w.chip[0]}`}><span aria-hidden="true" className={dot(w.chip[0])} />{w.chip[1]}</span>
                      </div>
                      <div className="sx-body">
                        <TourScenes ch={ch} step={step} tries={tries} onRetry={() => setTries((n) => Math.min(3, n + 1))} />
                      </div>
                      <div className={`sx-next${nx.who === "you" ? " you" : ""}`}>
                        <span aria-hidden="true" className={dot(nx.who)} />
                        <span className="sx-nxt">{nx.text}{nx.code && <> <code>{nx.code}</code></>}</span>
                        {nx.buttons.map(([label, cls]) => <span key={label} className={`sx-fake${cls ? ` ${cls}` : ""}`}>{label}</span>)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
