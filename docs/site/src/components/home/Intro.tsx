/** Under the hero: the agents QualityLayer works with, what it adds, one engineer's words, and the models you already pay for. */
import type { LucideIcon } from "lucide-react";
import { ArrowRight, BadgeCheck, FileText, KeyRound, Laptop, SquareTerminal, Workflow } from "lucide-react";
import { ENGINEER_QUOTE } from "@/lib/product";

type Chip = [label: string, icon: string];

const AGENTS: Chip[] = [
  ["Claude Code", "ast"],
  ["Codex", "braces"],
  ["Pi", "term"],
  ["OpenCode", "term"],
];

const MODELS: Chip[] = [
  ["Opus 5.5", "cpu"],
  ["Sonnet 5.5", "cpu"],
  ["Fable 5.1", "cpu"],
  ["Haiku 5.5", "cpu"],
  ["GPT-6.1 Sol", "cpu"],
  ["Claude Code", "ast"],
  ["Codex", "braces"],
  ["Pi", "term"],
  ["OpenCode", "term"],
];

const SETUPS: Chip[] = [
  ["Sonnet 5.5 writes the code", "term"],
  ["Opus 5.5 checks it", "file"],
  ["Codex reads the plan", "braces"],
  ["Claude Code reads the plan", "ast"],
  ["Or one agent does every step", "term"],
];

/** Each card in the App's colours: blue for the agent's work, amber for your decision, violet for what agents checked. */
const PRINCIPLES: { who: "agent" | "you" | "check"; icon: LucideIcon; title: string; lead: string; text: string }[] = [
  { who: "agent", icon: SquareTerminal, title: "Your agent", lead: "The tools you already use", text: "Your coding agent writes the code with the login you already have." },
  { who: "you", icon: Workflow, title: "One plan", lead: "Approved by you before any code", text: "Decisions as diagrams, screens as clickable mockups. Comment on any part." },
  { who: "check", icon: BadgeCheck, title: "Proof", lead: "Checked by an agent that did not write it", text: "Every test run is recorded and every agreed point is checked." },
];

/** From where you work to the files you keep: what QualityLayer connects, all inside one dashed frame, your computer. */
const CHAIN: { icon: LucideIcon | "mark"; title: string; text: string; chips: string[]; ql?: true }[] = [
  { icon: SquareTerminal, title: "Where you work", text: "Keep the tools you use today.", chips: ["Terminal", "Desktop app", "VS Code", "JetBrains"] },
  { icon: KeyRound, title: "Your agent, your subscription", text: "On the plan or API key you already pay for.", chips: ["Claude Code", "Codex", "Pi", "OpenCode"] },
  { icon: "mark", title: "QualityLayer", text: "A command line your agent calls, and the App where you decide.", chips: ["Command line", "The App"], ql: true },
  { icon: FileText, title: "Your repository", text: "Every step is a Markdown file you can read, diff and commit.", chips: ["Plan", "Decisions", "Test runs"] },
];

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
        <h2 id="with-h" className="mx-withp">Works with the agents you already use</h2>
        <ul className="mx-withg">
          {AGENTS.map(([label, icon]) => (
            <li key={label} className="mx-wi"><Icon name={icon} />{label}</li>
          ))}
        </ul>
        <p className="mx-with-other"><a href="/docs/agents/other">Other coding agents</a> can use the CLI.</p>
      </section>

      <section className="mx-sec" aria-labelledby="pr-h">
        <div className="mx-wrap">
          <div className="mx-head c">
            <h2 id="pr-h" className="mx-h2">Decided before it is built, proven after</h2>
            <p className="mx-lead">QualityLayer keeps your agent on every step, in order. You see only what needs you.</p>
          </div>
          <div className="mx-pr3">
            {PRINCIPLES.map(({ who, icon: Glyph, title, lead, text }) => (
              <div key={title} className="mx-pr" data-who={who}>
                <span className="mx-tile" aria-hidden="true"><Glyph size={20} strokeWidth={1.75} /></span>
                <h3>{title}</h3>
                <b>{lead}</b>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Right after the plan card it describes: the user's words as they said them, attributed without a name at their wish. */}
      <section className="mx-wrap mx-sec" aria-label="What an engineer says about QualityLayer">
        <figure className="mx-quote">
          <blockquote><p>{`“${ENGINEER_QUOTE}”`}</p></blockquote>
          <figcaption>An engineer who uses QualityLayer</figcaption>
        </figure>
      </section>

      <section id="local" className="mx-wrap mx-sec" aria-labelledby="local-h">
        <div className="mx-head c">
          <h2 id="local-h" className="mx-h2">Runs on your computer</h2>
          <p className="mx-lead">Keep your agent, editor and model plan. Nothing to host.</p>
        </div>
        <div className="mx-local">
          <span className="mx-local-tag"><Laptop size={15} strokeWidth={1.75} aria-hidden="true" />Your computer</span>
          <ol className="mx-chain">
            {CHAIN.map(({ icon: Glyph, title, text, chips, ql }, i) => (
              <li key={title} className={ql ? "ql" : undefined}>
                <span className="mx-tile" aria-hidden="true">{Glyph === "mark" ? <span className="mx-tile-mark" /> : <Glyph size={20} strokeWidth={1.75} />}</span>
                <b>{title}</b>
                <span className="mx-chain-text">{text}</span>
                <span className="mx-chain-chips">{chips.map((chip) => <span key={chip}>{chip}</span>)}</span>
                {i < CHAIN.length - 1 ? <span className="mx-chain-arrow" aria-hidden="true"><ArrowRight size={14} strokeWidth={2} /></span> : null}
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mx-wrap mx-sec" aria-labelledby="mod-h">
        <div className="mx-mq">
          <div className="mx-mqt">
            <h2 id="mod-h" className="mx-h3">Use the models you already pay for</h2>
            <p>Pick which model writes the code and which checks it. Choose Claude Code, Codex, Pi or OpenCode for a separate review of your plan and risky changes.</p>
          </div>
          <div className="mx-mqr">
            <p className="w7-sr">Models: {MODELS.filter(([, icon]) => icon === "cpu").map(([label]) => label).join(", ")}, through Claude Code, Codex, Pi and OpenCode. {SETUPS.map(([label]) => label).join(". ")}.</p>
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
