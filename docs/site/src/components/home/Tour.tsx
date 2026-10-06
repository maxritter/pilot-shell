import { ArrowLeft, BookOpen, ChevronDown, Expand, MessageSquare, MessageSquarePlus, Plus, Settings, SquareTerminal, Sun } from "lucide-react";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { CHAPTERS, PARTS, partOf, sidebarOf, statusOf, tabsOf, type Pill, type Who } from "@/lib/tour";
import TourScenes, { RightSide } from "./TourScenes";

/** The header's height; the window and the step bar pin below it. */
const HEADER = 68;
/** Widths where the window sits beside the chapters, and below which it gets its narrow phone layout. */
const WIDE = 1080;
const PHONE = 640;

const dot = (who: Who) => (who === "you" ? "sx-you" : who === "ok" ? "sx-ok" : "sx-ag");
const SETTINGS_TABS = ["Workflow", "Licence", "Team", "About"];

/** `inline`: below WIDE every chapter carries its own window; above it one window stays pinned beside the chapters. */
type Layout = { lw: number; lh: number; sc: number; side: boolean; inline: boolean };

const reducedMotion = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
const finished = () => CHAPTERS.map((c) => c.steps);

type WinProps = { i: number; step: number; tries: number; onRetry: () => void; layout: Layout; only?: boolean };

/** The live status in the task header: needs you here, an agent at work, your move outside the App, or done. */
function StatusPill({ pill, compact = false }: { pill: Pill; compact?: boolean }) {
  return (
    <span className={`sx-pill ${pill.kind}${compact ? " compact" : ""}`}>
      {pill.kind === "ag" && <span aria-hidden="true" className="sx-ag" />}
      {pill.kind === "move" && <SquareTerminal size={12} aria-hidden="true" />}
      <b>{pill.head}</b>
      {pill.text && !compact && <span>· {pill.text}</span>}
      {pill.meta && !compact && <em>{pill.meta}</em>}
      <ChevronDown size={12} aria-hidden="true" />
    </span>
  );
}

/** The App window showing chapter `i` at moment `step`: sidebar, header with the step's file and the status, the five steps, what needs you, the scene. */
function AppWindow({ i, step, tries, onRetry, layout, only = false }: WinProps) {
  const c = CHAPTERS[i], w = c.win;
  const task = w.view === "task";
  const design = w.view === "design";
  const status = task || design ? statusOf(i, step) : null;
  const tabs = tabsOf(i, step);
  const { lw, lh, sc, side } = layout;
  const right = side && task ? w.right : undefined;
  return (
    <div role="region" aria-label={`The QualityLayer App: ${c.title}`} className="sx-win" style={{ width: Math.round(lw * sc) + 2 }}>
      <div className="sx-bar" aria-hidden="true"><i /><i /><i /><span>{w.title}</span></div>
      {/* An illustration of the App; the chapter beside it says the same in words. */}
      <div className="sx-fit" aria-hidden="true" style={{ height: Math.round(lh * sc) }}>
        <div className={`sx-scale${side ? "" : " sx-nw"}${right ? " sx-rson" : ""}${c.id === "plan" && step >= 4 ? " sx-planfull" : ""}`} style={{ width: lw, height: lh, transform: `scale(${sc})` }}>
          {side && (
            <aside className="sx-side">
              <p className="sx-sbrand"><span aria-hidden="true" className="sx-mark" />QualityLayer<span className={`sx-new${c.id === "agents" ? " on" : ""}`}><Plus size={11} />New</span></p>
              {w.switch && (
                <div className="sx-sw"><span className={w.switch === "personal" ? "on" : ""}>Personal</span><span className={w.switch === "team" ? "on" : ""}>Team</span></div>
              )}
              <span className="sx-find">{w.switch === "team" ? "Search the team’s tasks" : "Search or jump to a task"}<kbd>⌘K</kbd></span>
              {sidebarOf(i, step).map((g) => (
                <div key={g.label} className="sx-grp">
                  <p className={`sx-sg${g.amber && g.count > 0 ? " amb" : ""}`}><span>{g.label}</span><b>{g.count}</b></p>
                  {g.items.map((t) => (
                    <div key={t.name} className={`sx-ti${t.on ? " on" : ""}`}>
                      <span aria-hidden="true" className={dot(t.who)} />
                      <span className="sx-tin"><b>{t.name}</b><small>{t.sub}</small></span>
                    </div>
                  ))}
                </div>
              ))}
              <div className="sx-sfoot">
                {c.id === "agents" && <span className="sx-upd"><span aria-hidden="true" className="sx-udot" /><b>Update ready</b><small>Restart</small></span>}
                <div className="sx-me"><span className="sx-avm">{w.foot[0].split(" ").map((n) => n[0]).join("")}</span><span className="sx-tin"><b>{w.foot[0]}</b><small>{w.foot[1]}</small></span></div>
                <div className="sx-icons">
                  <span className={`sx-ib${w.view === "settings" ? " on" : ""}`}><Settings size={15} /></span>
                  <span className="sx-ib"><BookOpen size={15} /></span>
                  <span className="sx-ib"><Sun size={15} /></span>
                  <span className="sx-fb"><MessageSquare size={14} />Feedback</span>
                </div>
              </div>
            </aside>
          )}
          <div className="sx-main">
            {design && status && (
              // A design open full size: one thin bar over the whole content area.
              <div className="sx-dbar">
                <span className="sx-dback"><ArrowLeft size={13} />Back to the Plan</span>
                <i className="sx-dsep" />
                <b className="sx-dname">{w.doc}</b>
                <small className="sx-hide">Updated {step >= 5 ? "just now" : "3 min ago"}</small>
                <span className="sx-grow" />
                <StatusPill pill={status.pill} compact />
                <span className={`sx-dbtn${step >= 1 && step < 3 ? " on" : ""}`}><MessageSquarePlus size={13} />Comment<kbd>C</kbd></span>
                <span className="sx-dbtn sx-hide">Jump to<ChevronDown size={12} /></span>
                <span className="sx-dicon sx-hide" title="Full screen"><Expand size={13} /></span>
              </div>
            )}
            {task && status ? (
              <div className="sx-taskbar">
                <b className="sx-taskname">{w.doc}</b>
                <ol className="sx-track" aria-label="Steps of this task">
                  {tabs.map((t) => <li key={t.label} className={t.mark === "you" || t.mark === "ag" ? "cur" : ""}>{t.label}</li>)}
                </ol>
                <StatusPill pill={status.pill} />
                {status.turn && <span className="sx-turn-pill"><i className="sx-you" />Your turn<small> · {status.turn}</small></span>}
                <span className="sx-taskmenu" aria-hidden="true">···</span>
              </div>
            ) : !design && (
              <div className="sx-mh">
                <div className="sx-mhl">
                  <p className="sx-mt">{w.doc}</p>
                  {w.sub && <p className="sx-sub">{w.sub}</p>}
                </div>
              </div>
            )}
            {w.view === "settings" && (
              <ol className="sx-tabs" aria-label="Settings">
                {SETTINGS_TABS.map((t, k) => <li key={t} className={`sx-tab${k === 0 ? " cur" : ""}`}>{t}</li>)}
              </ol>
            )}
            <div className="sx-taskcontent">
              <div className="sx-body">
                <TourScenes ch={i} step={step} tries={tries} onRetry={onRetry} only={only} />
              </div>
              {right && <RightSide ch={i} step={step} tab={right} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * One change followed from request to pull request, then the team and the setup. On wide screens
 * the chapters scroll on the left while the App window stays pinned on the right. On tablets and
 * phones each chapter carries its own window, which plays its scene as it scrolls into view, and
 * only the step bar pins under the header. Text and windows fade with their place on screen.
 */
export default function Tour() {
  const [ch, setCh] = useState(0);
  // Each chapter's moment. With reduced motion every scene shows complete.
  const [steps, setSteps] = useState<number[]>(() => (reducedMotion() ? finished() : CHAPTERS.map(() => 0)));
  const [tries, setTries] = useState(2);
  const [layout, setLayout] = useState<Layout>({ lw: 940, lh: 600, sc: 0.8, side: true, inline: false });

  const tourRef = useRef<HTMLElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const dockRef = useRef<HTMLDivElement>(null);
  const stepsRef = useRef<HTMLOListElement>(null);
  const chsRef = useRef<HTMLDivElement>(null);
  const chRef = useRef(0);
  // The scroll handler reads the layout without waiting for a render.
  const layoutRef = useRef(layout);

  /** Make chapter `i` current. The pinned window replays its scene; an inline window carries on where it was, unless asked to start over. */
  const play = useCallback((i: number, again = false) => {
    chRef.current = i;
    setCh(i);
    setTries(2);
    if (reducedMotion()) return;
    if (again || !layoutRef.current.inline) setSteps((s) => s.map((v, k) => (k === i ? 0 : v)));
  }, []);

  // The current scene's parts appear one per second.
  const step = steps[ch];
  useEffect(() => {
    if (reducedMotion() || step >= CHAPTERS[ch].steps) return;
    const id = setTimeout(() => setSteps((s) => s.map((v, k) => (k === ch ? v + 1 : v))), 1000);
    return () => clearTimeout(id);
  }, [ch, step]);

  // Fit the window: a fixed inner size, scaled to its column. Phones get their own narrow layout.
  const measure = useCallback(() => {
    const stage = stageRef.current, chs = chsRef.current;
    if (!stage || !chs) return;
    const rw = document.documentElement.clientWidth, vh = window.innerHeight;
    let next: Layout;
    if (rw >= WIDE) next = { lw: 940, lh: 600, side: true, inline: false, sc: Math.min(stage.clientWidth / 940, (vh - 96 - HEADER) / 600) };
    else if (rw > PHONE) next = { lw: 940, lh: 600, side: true, inline: true, sc: Math.min(chs.clientWidth / 940, (vh * 0.62) / 600) };
    else next = { lw: 400, lh: 540, side: false, inline: true, sc: Math.min(chs.clientWidth / 400, (vh * 0.62) / 540) };
    next.sc = Math.max(0.3, Math.round(next.sc * 1000) / 1000);
    const cur = layoutRef.current;
    if (cur.lw !== next.lw || cur.lh !== next.lh || cur.sc !== next.sc || cur.side !== next.side || cur.inline !== next.inline) {
      layoutRef.current = next;
      setLayout(next);
    }
  }, []);

  // On wide screens the window starts large and centred under the hero, then settles into its column as you scroll.
  const dockFrame = useCallback(() => {
    const tour = tourRef.current, stage = stageRef.current, dock = dockRef.current, bar = stepsRef.current, chs = chsRef.current;
    if (!tour || !stage) return;
    const y = window.scrollY;
    if (dock && !layoutRef.current.inline && !reducedMotion()) {
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
      if (dock) dock.style.transform = "";
      if (bar) bar.style.opacity = "";
      if (chs) chs.style.opacity = "";
    }
  }, []);

  /**
   * The current chapter. Beside the pinned window: the chapter nearest a line a little above
   * mid-screen. Inline: the last chapter whose window has risen past 70 % of the screen, so its
   * scene plays while most of it is in view.
   */
  const current = useCallback(() => {
    const tour = tourRef.current;
    if (!tour) return chRef.current;
    const vh = window.innerHeight;
    if (layoutRef.current.inline) {
      let best = 0;
      tour.querySelectorAll(".sx-ch").forEach((el, i) => {
        const win = el.querySelector(".sx-iwin") ?? el;
        if (win.getBoundingClientRect().top <= vh * 0.7) best = i;
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

  // Per scroll frame: the window's position, then the current chapter.
  const frame = useCallback(() => {
    dockFrame();
    const tour = tourRef.current;
    if (!tour) return;
    const tr = tour.getBoundingClientRect();
    if (tr.bottom < 0 || tr.top > window.innerHeight) return;
    const best = current();
    if (best !== chRef.current) play(best);
  }, [dockFrame, current, play]);

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

  // A new scale changes the window's size, so its docked position is measured again.
  useLayoutEffect(() => {
    dockFrame();
  }, [layout, dockFrame]);

  // Keep the current chapter visible in the step bar when it scrolls sideways.
  useEffect(() => {
    const bar = stepsRef.current, cur = bar?.querySelector<HTMLElement>(".sx-step.on");
    if (bar && cur) bar.scrollLeft = cur.offsetLeft - (bar.clientWidth - cur.offsetWidth) / 2;
  }, [ch]);

  const goTo = (i: number) => {
    const tour = tourRef.current;
    const behavior = reducedMotion() ? "auto" : "smooth";
    if (!tour) return;
    if (layoutRef.current.inline) {
      const el = tour.querySelectorAll(".sx-ch")[i];
      if (!el) return;
      const under = HEADER + (stageRef.current?.offsetHeight ?? 0) + 12;
      window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - under, behavior });
      return;
    }
    const el = tour.querySelectorAll(".sx-chin")[i];
    if (!el) return;
    const r = el.getBoundingClientRect();
    window.scrollTo({ top: r.top + window.scrollY - (window.innerHeight * 0.4 - r.height / 2), behavior });
  };

  const part = partOf(ch);
  const retry = () => setTries((n) => Math.min(3, n + 1));
  const { inline } = layout;

  return (
    <div className="sx-root">
      <section id="tour" ref={tourRef} className={`sx-tour${inline ? " sx-inl" : ""}`} aria-labelledby="tour-h">
        <h2 id="tour-h" className="w7-sr">How one change goes from request to pull request</h2>
        <div ref={chsRef} className="sx-chs">
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
                    <div className="sx-iwin sx-rvw">
                      <AppWindow i={i} step={steps[i]} tries={i === ch ? tries : 2} onRetry={retry} layout={layout} only />
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

            {!inline && (
              <div ref={dockRef} className="sx-dock">
                <AppWindow i={ch} step={step} tries={tries} onRetry={retry} layout={layout} />
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
