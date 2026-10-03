import { useEffect, useRef, useState } from "react";
import { useTheme, type Theme } from "@/hooks/useTheme";
import { STOPS, useDemoTour, type DemoRoute, type Who } from "./demoTour";

const DEMO_SRC = "/app-demo/index.html";
const dot = (who?: Who) => (who === "you" ? "w7-you" : "w7-ag");

function paintTheme(frame: HTMLIFrameElement | null, theme: Theme) {
  const root = frame?.contentDocument?.documentElement;
  if (!root) return;
  root.dataset.theme = theme;
  root.classList.toggle("dark", theme === "dark");
}

/** The real App, fed illustrative tasks, with a tour bar above it. Laptops and tablets only. */
export default function CockpitTour() {
  const tour = useDemoTour();
  const frame = useRef<HTMLIFrameElement>(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const { observe } = tour;
  const { theme } = useTheme();

  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return;
      if (event.data?.type === "qualitylayer-demo-ready") {
        setReady(true);
        setFailed(false);
      }
      if (event.data?.type === "qualitylayer-demo-route") observe(event.data.route as DemoRoute);
    };
    window.addEventListener("message", receive);
    return () => window.removeEventListener("message", receive);
  }, [observe]);

  useEffect(() => {
    if (ready) frame.current?.contentWindow?.postMessage({ type: "qualitylayer-demo-open", route: tour.route }, window.location.origin);
  }, [ready, tour.route, tour.revision]);

  // The demo is served from this origin, so it can wear the page's light or dark theme.
  useEffect(() => {
    if (ready) paintTheme(frame.current, theme);
  }, [ready, theme]);

  const stop = STOPS[tour.stop];
  const moment = stop.moments[tour.moment] ?? stop.moments[0];
  const caption = tour.exploring ? { context: "Exploring on your own.", hint: "Pick a stop above to rejoin the tour." } : moment;
  const side = (id: string, icon: string) => {
    const i = STOPS.findIndex((s) => s.id === id);
    const on = i === tour.stop && !tour.exploring;
    return (
      <button type="button" onClick={() => tour.select(i)} aria-pressed={on} className={`v8-side${on ? " on" : ""}`}>
        <span aria-hidden="true" className={`v8-ico v8-ico-${icon}`} />
        {STOPS[i].label}
      </button>
    );
  };
  const stages = STOPS.map((s, i) => ({ s, i })).filter(({ s }) => !s.side);

  return (
    <section id="app" className="w7-cockpit" aria-labelledby="cockpit-h">
      <div className="w7-cockpit-wrap">
        <div className="w7-cockpit-head">
          <div>
            <h2 id="cockpit-h">Try the App</h2>
            <p>Where you review and approve your agent’s work. This demo is fully clickable, with example tasks.</p>
          </div>
          <div className="w7-cockpit-key">
            <span><span aria-hidden="true" className="w7-you" />Your move</span>
            <span><span aria-hidden="true" className="w7-ag" />Agent working</span>
          </div>
        </div>

        <div role="group" aria-label="Tour of the App" className="v8-tbar">
          {side("queue", "queue")}
          <span aria-hidden="true" className="v8-tsep" />
          <ol className="v8-stages" aria-label="Stages">
            {stages.map(({ s, i }) => {
              const on = i === tour.stop && !tour.exploring;
              return (
                <li key={s.id} className="v8-sli">
                  <button type="button" onClick={() => tour.select(i, s.moments.length - 1)} aria-pressed={on} className={`v8-stage${on ? " on" : ""}`}>
                    <span aria-hidden="true" className={dot(s.who)} />
                    {s.label}
                  </button>
                </li>
              );
            })}
          </ol>
          <span aria-hidden="true" className="v8-tsep" />
          {side("team", "team")}
          {side("settings", "gear")}
        </div>

        <div className="v8-cap">
          {!tour.exploring && stop.moments.length > 1 ? (
            <div role="group" aria-label={`${stop.label}: moment`} className="v8-sseg">
              {stop.moments.map((m, j) => (
                <button key={m.label} type="button" onClick={() => tour.select(tour.stop, j)} aria-pressed={j === tour.moment} className={`v8-sb${j === tour.moment ? " on" : ""}`}>
                  <span aria-hidden="true" className={dot(m.who)} />
                  {m.label}
                </button>
              ))}
            </div>
          ) : null}
          <p aria-live="polite" className="v8-capt">
            <span className="w7-cap-ctx">{caption.context}</span>
            <span className="w7-cap-try"><b>Try · </b>{caption.hint}</span>
          </p>
        </div>

        <div className="w7-window">
          <div className="w7-window-bar">
            <span aria-hidden="true" className="w7-window-dots"><i /><i /><i /></span>
            <span className="w7-window-title">QualityLayer App · runs on your machine</span>
            <span className="w7-window-note">illustrative data</span>
          </div>
          {failed ? (
            <div className="w7-demo-error" role="alert">
              <p>The demo could not load.</p>
              <button type="button" className="w7-btn-s" onClick={() => { setFailed(false); setReady(false); if (frame.current) frame.current.src = DEMO_SRC; }}>Try again</button>
            </div>
          ) : null}
          <iframe ref={frame} src={DEMO_SRC} title="Interactive QualityLayer App with illustrative tasks" className="w7-demo-frame" loading="lazy" onError={() => setFailed(true)} />
        </div>
      </div>
    </section>
  );
}
