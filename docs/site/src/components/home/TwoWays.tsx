import { useEffect, useRef, useState, type CSSProperties } from "react";

/**
 * Two timelines side by side in time: planning and building with QualityLayer, and the usual way.
 * The wide version draws a 24-unit timeline; phones get the same story as a list of steps.
 */

type Part = "plan" | "build";
type Bar = { cls: string; l: string; w: string; text: string; art: boolean };
type Feedback = { l: string; who: { cls: string; i: string; t: string }[] };
type Row = { name: string; sub: string; items: Bar[]; h: string; fbs: Feedback[] };
type Overlay = { cls: string; l: string; w: string; t: string; h: string; text: string };
type Card = { cls: string; l: string; w: string; t: string; title: string; ok: string; status: string; ev: { icon: string; name: string }[] };
/** A phone step: colour kind, title, subline, chips [kind, text], and whether you approve there. */
type Step = [kind: string, title: string, sub: string, chips: [string, string][] | null, gate: boolean];

const U = 24;
const pct = (u: number) => `${((u / U) * 100).toFixed(3)}%`;
const it = (cls: string, a: number, b: number, text = "", art = false): Bar => ({ cls, l: pct(a), w: pct(Math.max(b - a, 0)), text, art });
const at = (cls: string, u: number, text = ""): Bar => ({ cls, l: pct(u), w: "", text, art: false });
const fb = (u: number, who: [string, string, string][]): Feedback => ({ l: pct(u), who: who.map(([c, i, t]) => ({ cls: `tw-who ${c}`, i, t })) });
// Geometry for overlays: label column 112px + 22px padding; axis row 44px tall with its 10px top padding.
const LEFT = 134;
const R = 46;
const TOP = 10 + 34;
const x = (u: number) => `calc(${LEFT}px + (100% - ${LEFT + 22}px) * ${(u / U).toFixed(4)})`;
const w = (a: number, b: number) => `calc((100% - ${LEFT + 22}px) * ${((b - a) / U).toFixed(4)})`;
const row = (name: string, sub: string, items: Bar[], h = R, fbs: Feedback[] = []): Row => ({ name, sub, items, h: `${h}px`, fbs });

function timeline(part: Part, ql: boolean) {
  let rows: Row[];
  let overlays: Overlay[] = [];
  let cards: Card[] = [];
  let from: string;
  let to: string;
  let aria: string;
  if (part === "plan") {
    from = "request";
    to = ql ? "plan approved" : "coding starts";
    rows = ql ? [
      row("Goal", "what done means", [it("tw-b ag", 0, 3.4, "Agent asks"), it("tw-line", 0.6, 3.8), at("tw-gate", 3.8)]),
      row("Research", "what exists", [it("tw-b ag", 4.2, 8.4, "Helpers read the code"), it("tw-line", 4.8, 8.8), at("tw-gate", 8.8)]),
      row("Design", "what to build", [it("tw-b ag draft", 9.2, 11.8, "Draft 1", true), it("tw-b ag draft", 12.6, 15.2, "Draft 2", true), it("tw-b ag draft", 16, 18.4, "Draft 3", true), at("tw-gate", 18.8)], 112,
        [fb(12.2, [["tw-wy", "Y", "You"], ["tw-wt", "B", "Ben"]]), fb(15.6, [["tw-wa", "AI", "Second AI"], ["tw-wt", "A", "Anna"]])]),
      row("Outline", "how to split it", [it("tw-b ag", 19.2, 23, "Slices, double-checked"), it("tw-line", 19.8, 23.4), at("tw-gate", 23.4)]),
    ] : [
      row("Chat", "the plan", [it("tw-b ag", 0, 3, "A prompt")]),
      row("You", "reviewer", [at("tw-note", 3.6, "Nothing to review: no diagram, no mockup, no plan to read")]),
    ];
    aria = ql
      ? "Each document is reviewed from its first draft; the design goes through three drafts with diagrams and mockups, revised after comments from you, teammates and a second AI"
      : "The plan is a prompt in the chat, with nothing to review";
  } else {
    from = "";
    to = "merged";
    const S: [number, number, string, string, string][] = ql
      ? [[0.2, 5, "s1", "Slice 1", "One job type moves"], [5.8, 10.6, "s2", "Slice 2", "The switch panel"], [11.4, 16.2, "s3", "Slice 3", "Payment capture"]]
      : [[0.2, 5.6, "s1", "Slice 1", "One job type moves"], [6.6, 12, "s2", "Slice 2", "The switch panel"], [13, 18.4, "s3", "Slice 3", "Payment capture"]];
    const layers = ["Screen", "API", "Logic", "Data", "Tests"];
    if (ql) {
      rows = layers.map((n) => row(n, "", S.map((s) => it(`tw-b ${s[2]}`, s[0], s[1])))).concat([
        row("Checked", "end to end", [], 108),
        row("Simplify", "whole change", [it("tw-b simp", 16.6, 18.8, "Simplify")]),
        row("Check", "whole change", [it("tw-b judge", 18.8, 22, "Independent check")]),
        row("You", "final review", [it("tw-b you", 22.2, 24, "Review")]),
      ]);
      overlays = S.map((s) => ({ cls: `tw-col ${s[2]}`, l: x(s[0] - 0.2), w: w(s[0] - 0.2, s[1] + 0.2), t: `${TOP + 4}px`, h: `${5 * R - 8}px`, text: `${s[3]} · ${s[4]}` }));
      const ev = [{ icon: "tw-ei t", name: "Tests" }, { icon: "tw-ei l", name: "Logs" }, { icon: "tw-ei s", name: "Screenshot" }];
      const card = (k: number, title: string, ok: string, status: string): Card => ({
        cls: `tw-card ${S[k][2]}`, l: x(S[k][0] - 0.2), w: w(S[k][0] - 0.2, S[k][1] + 0.2), t: `${TOP + 5 * R + 8}px`, title, ok, status, ev });
      cards = [
        card(0, "First run end to end", "Passed", "Scenario 1 · a job moves"),
        card(1, "End-to-end check", "Passed", "Scenario 2 · switch and back"),
        card(2, "End-to-end check", "Run 2 passed", "Run 1 failed, fixed at the source"),
      ];
    } else {
      rows = [
        row("Screen", "", [it("tw-b ly", 13.5, 17, "All screens"), it("tw-b re", 21.8, 24)]),
        row("API", "", [it("tw-b ly", 10, 13.8, "All endpoints"), it("tw-b re", 21.8, 24)]),
        row("Logic", "", [it("tw-b ly", 5, 10.3, "All services"), it("tw-b re", 21.8, 24)]),
        row("Data", "", [it("tw-b ly", 0, 5.3, "All tables"), it("tw-b re", 21.8, 24, "Rework")]),
        row("Tests", "", [it("tw-b ly", 16.8, 18.6, "Tests")]),
        row("Runs?", "end to end", [at("tw-cp", 18.8), at("tw-chip bad", 18.8, "Fails")]),
        row("You", "review", [it("tw-b you", 19.2, 21.6, "One large diff")]),
      ];
      overlays = [{ cls: "tw-mark", l: x(18.8), w: "0", t: `${TOP}px`, h: "auto", text: "First time it runs" }];
    }
    aria = ql
      ? "Three vertical slices in three colours, each through every layer; each ends with an end-to-end check that keeps test output, logs and a screenshot; then one pass that simplifies the whole change; then an independent check and your final review"
      : "Tables, then services, then endpoints, then screens, tests last; the first run is at the end and fails, and every layer is reworked";
  }
  return { rows, overlays, cards, from, to, aria };
}

const L = ["Screen", "API", "Logic", "Data", "Tests"].map((t): [string, string] => ["", t]);
const STEPS: Record<Part, Record<"ql" | "usual", Step[]>> = {
  plan: {
    ql: [
      ["ag", "Goal", "The agent asks what done means", null, true],
      ["ag", "Research", "Helpers read the code first", null, true],
      ["ag", "Design · three drafts", "Diagrams and mockups, revised after each round of comments", [["who-you", "You"], ["", "Ben"], ["who-ai", "Second AI"], ["", "Anna"]], true],
      ["ag", "Outline", "Slices, double-checked", null, true],
      ["end", "Plan approved, no code yet", "", null, false],
    ],
    usual: [
      ["ly", "A prompt in the chat", "That is the whole plan", null, false],
      ["bad", "Nothing to review", "No diagram, no mockup, no plan to read", null, false],
      ["end", "Coding starts", "", null, false],
    ],
  },
  build: {
    ql: [
      ["s1", "Slice 1 · one job type moves", "Runs end to end: passed", L, false],
      ["s2", "Slice 2 · the switch panel", "Runs end to end: passed", L, false],
      ["s3", "Slice 3 · payment capture", "Run 1 failed, fixed at the source; run 2 passed", L, false],
      ["simp", "Simplify", "One pass makes the whole change simpler", null, false],
      ["judge", "Independent check", "An AI that did not write it checks your request", null, false],
      ["you", "Your final review", "With the evidence: tests, logs, screenshots", null, true],
      ["end", "Merged", "", null, false],
    ],
    usual: [
      ["ly", "All tables, then services", "", null, false],
      ["ly", "Then endpoints, then screens", "", null, false],
      ["ly", "Tests last", "", null, false],
      ["bad", "First run end to end: fails", "Rework in every layer", null, false],
      ["you", "One large diff to review", "", null, false],
      ["end", "Merged", "", null, false],
    ],
  },
};

const KEYS: Record<Part, Record<"ql" | "usual", [string, string][]>> = {
  plan: {
    ql: [
      ["Diagrams and mockups", "The agent shows the design as diagrams and mockups you can click through."],
      ["Comments become a new draft", "Your comments reach the agent while it writes, and it revises the same document."],
      ["More than one reviewer", "Teammates and an AI from another vendor review the same draft. You approve it."],
    ],
    usual: [
      ["The plan is a chat", "Nobody reviews it, so nobody can catch a wrong scope."],
      ["Review starts at the pull request", "You see the design for the first time inside a large diff."],
    ],
  },
  build: {
    ql: [
      ["Thin vertical slices", "Each one goes through every layer, built test-first by a smaller, cheaper model."],
      ["Tested before the next one", "The whole program runs end to end after every slice, and the tests, logs and screenshots are kept."],
      ["Simpler at the end", "One pass merges near-copies, reuses code you already have and removes what isn’t needed. Behaviour stays the same."],
      ["An independent final check", "An AI that did not write the code reruns every test and scenario against your request, and undoes a simplification that broke something."],
    ],
    usual: [
      ["Layer by layer", "All tables, then services, then endpoints, then screens."],
      ["It runs at the end", "The first end-to-end run comes last, and fails."],
      ["Nobody cleans up", "Copies, extra wrappers and dead ends stay in the code and slow down the next change."],
      ["Rework everywhere", "A fix touches every layer, inside one large diff."],
    ],
  },
};

type Anim = "idle" | "hide" | "go";

export default function TwoWays({ part }: { part: Part }) {
  const [ql, setQl] = useState(true);
  const [anim, setAnim] = useState<Anim>("idle");
  const root = useRef<HTMLDivElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // The timeline draws itself from left to right, once when it comes into view and on Replay.
  const sweep = () => {
    clearTimeout(timer.current);
    setAnim("hide");
    timer.current = setTimeout(() => setAnim("go"), 60);
  };

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window) || !root.current) return;
    setAnim("hide");
    const io = new IntersectionObserver((entries) => {
      if (entries[0]?.isIntersecting) {
        io.disconnect();
        sweep();
      }
    }, { threshold: 0.3 });
    io.observe(root.current);
    return () => {
      io.disconnect();
      clearTimeout(timer.current);
    };
  }, []);

  const pick = (next: boolean) => {
    setQl(next);
    sweep();
  };
  const { rows, overlays, cards, from, to, aria } = timeline(part, ql);
  const mode = ql ? "ql" : "usual";
  const keys = KEYS[part][mode];

  return (
    <div className="tw" ref={root}>
      <div className="tw-top">
        <div role="group" aria-label="Compare" className="tw-seg">
          <button type="button" onClick={() => pick(true)} aria-pressed={ql} className={`tw-sb ql${ql ? " on" : ""}`}>With QualityLayer</button>
          <button type="button" onClick={() => pick(false)} aria-pressed={!ql} className={`tw-sb${ql ? "" : " on"}`}>The usual way</button>
        </div>
        <button type="button" onClick={sweep} className="tw-replay">Replay</button>
      </div>

      <div className="tw-panel">
        <div className="tw-g" role="img" aria-label={aria}>
          <div className="tw-axis" aria-hidden="true" style={{ gridRow: 1 }}><span>{from}</span><span>{to}</span></div>
          {rows.map((r, i) => {
            const at: CSSProperties = { gridRow: i + 2, minHeight: r.h };
            return (
              <div key={r.name} style={{ display: "contents" }}>
                <div className="tw-rl" style={at}><b>{r.name}</b><span>{r.sub}</span></div>
                <div className="tw-row" style={at}>
                  {r.items.map((b, k) => (
                    <span key={k} className={b.cls} style={{ left: b.l, width: b.w || undefined }}>
                      {b.art ? <><span aria-hidden="true" className="tw-art dg" /><span aria-hidden="true" className="tw-art mk" /></> : null}
                      {b.text}
                    </span>
                  ))}
                  {r.fbs.map((f) => (
                    <div key={f.l} className="tw-fb" style={{ left: f.l }}>
                      <div className="tw-fbr">{f.who.map((p) => <span key={p.t} className={p.cls}><i>{p.i}</i>{p.t}</span>)}</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
          {overlays.map((o) => (
            <div key={o.text} aria-hidden="true" className={o.cls} style={{ left: o.l, width: o.w, top: o.t, height: o.h }}><span className="tw-ol">{o.text}</span></div>
          ))}
          {cards.map((c) => (
            <div key={c.status} className={c.cls} style={{ left: c.l, width: c.w, top: c.t }}>
              <div className="tw-ch"><b>{c.title}</b><span className="tw-ok">{c.ok}</span></div>
              <span className="tw-cs">{c.status}</span>
              <div className="tw-ev">{c.ev.map((e) => <span key={e.name} className="tw-e"><span aria-hidden="true" className={e.icon} />{e.name}</span>)}</div>
            </div>
          ))}
          <div aria-hidden="true" className={`tw-cover${anim === "hide" ? " hide" : anim === "go" ? " go" : ""}`} />
        </div>
      </div>

      <ol className="tw-m" aria-label={aria}>
        {STEPS[part][mode].map(([kind, title, sub, chips, gate]) => (
          <li key={title} className={`tw-mi tw-m-${kind}`}>
            <span aria-hidden="true" className="tw-md" />
            <div className="tw-mc">
              <b>{title}</b>
              {sub ? <span className="tw-ms">{sub}</span> : null}
              {chips ? <span className="tw-mchips">{chips.map(([c, t]) => <span key={t} className={`tw-mch${c ? ` tw-m-${c}` : ""}`}>{t}</span>)}</span> : null}
              {gate ? <span className="tw-mgate">You approve</span> : null}
            </div>
          </li>
        ))}
      </ol>

      <ul className={`tw-keys${keys.length % 2 === 0 ? " two" : ""}`}>
        {keys.map(([title, text]) => <li key={title} className="tw-k"><b>{title}</b><span>{text}</span></li>)}
      </ul>
    </div>
  );
}
