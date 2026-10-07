/** Under the hero: the agents QualityLayer works with, what it adds, and the models you already pay for. */

type Chip = [label: string, icon: string];

const AGENTS: Chip[] = [
  ["Claude Code", "ast"],
  ["Codex", "braces"],
  ["Terminal", "term"],
  ["Desktop apps", "app"],
  ["VS Code", "code"],
  ["JetBrains", "code"],
];

const MODELS: Chip[] = [
  ["Opus 5.5", "cpu"],
  ["Sonnet 5.5", "cpu"],
  ["Fable 5.1", "cpu"],
  ["Haiku 4.5", "cpu"],
  ["GPT-6.1 Sol", "cpu"],
  ["Claude Code", "ast"],
  ["Codex", "braces"],
];

const SETUPS: Chip[] = [
  ["Sonnet 5.5 writes the code", "term"],
  ["Opus 5.5 checks it", "file"],
  ["Codex reviews risky plans", "braces"],
  ["Claude Code reviews risky plans", "ast"],
  ["Or one agent does every step", "term"],
];

const PRINCIPLES = [
  ["Your agent", "The tools you already trust", "Claude Code or Codex writes the code in its own terminal, app or editor, on your subscription."],
  ["One plan", "Approved by you before any code", "Every decision shown as it will look: a clickable mockup and a diagram you can comment on."],
  ["Proof", "Checked by agents that did not write it", "Every test run recorded, every point of Done means checked, and the proof one click away."],
] as const;

const Icon = ({ name }: { name: string }) => <i className={`mx-ic mx-i-${name}`} aria-hidden="true" />;

/** One drifting row. The chips are listed twice so the loop has no seam; screen readers get the sentence beside it instead. */
const Track = ({ chips, reverse }: { chips: Chip[]; reverse?: boolean }) => (
  <div className={reverse ? "mx-track rev" : "mx-track"}>
    {[...chips, ...chips].map(([label, icon], i) => (
      <span key={`${label}-${i}`} className="mx-chip">
        <Icon name={icon} />
        {label}
      </span>
    ))}
  </div>
);

export default function Intro() {
  return (
    <>
      <section id="agents" className="mx-with" aria-labelledby="with-h">
        <h2 id="with-h" className="mx-withp">Works with the agents you already use, wherever you run them</h2>
        <ul className="mx-withg">
          {AGENTS.map(([label, icon]) => (
            <li key={label} className="mx-wi"><Icon name={icon} />{label}</li>
          ))}
        </ul>
      </section>

      <section className="mx-sec" aria-labelledby="pr-h">
        <div className="mx-wrap">
          <div className="mx-head c">
            <h2 id="pr-h" className="mx-h2">Decided before it is built, proven after</h2>
            <p className="mx-lead">QualityLayer holds the workflow, so your agent never skips a step. You see only what needs a person.</p>
          </div>
          <div className="mx-pr3">
            {PRINCIPLES.map(([title, lead, text]) => (
              <div key={title} className="mx-pr">
                <h3>{title}</h3>
                <b>{lead}</b>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-wrap mx-sec" aria-labelledby="mod-h">
        <div className="mx-mq">
          <div className="mx-mqt">
            <h2 id="mod-h" className="mx-h3">Use the models you already pay for</h2>
            <p>Choose which model writes the code and which one checks it, in Claude Code and Codex. On a risky plan, the other coding agent reviews it too.</p>
          </div>
          <div className="mx-mqr">
            <p className="w7-sr">Models: {MODELS.filter(([, icon]) => icon === "cpu").map(([label]) => label).join(", ")}, through Claude Code and Codex. {SETUPS.map(([label]) => label).join(". ")}.</p>
            <div className="mx-mqm" aria-hidden="true">
              <Track chips={MODELS} />
              <Track chips={SETUPS} reverse />
            </div>
            <p className="mx-mqn">+ any model your coding agent offers</p>
          </div>
        </div>
      </section>
    </>
  );
}
