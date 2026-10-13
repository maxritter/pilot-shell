import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Expand, ExternalLink, House, PenTool, SlidersHorizontal, Users, X, type LucideIcon } from "lucide-react";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useNarrow } from "@/hooks/useNarrow";
import { useTheme } from "@/hooks/useTheme";
import { FILMS } from "@/lib/films";
import "@/styles/editorial.css";

/** Who acts in a step, in the App's colours: amber when you decide, blue when agents work, violet when agents check. */
type Who = "you" | "agent" | "check";
type Shot = { id: string; title: string; alt: string };
type Item = { id: string; name: string; who?: Who; icon?: LucideIcon; line: string; text: string; shot: Shot; link?: { to: string; label: string } };

const WHO: Record<Who, string> = { you: "You decide", agent: "Agents work", check: "Agents check" };

const STEPS: Item[] = [
  { id: "discuss", name: "Discuss", who: "you", line: "Settle what you want", text: "Your agent asks only questions that change the result, each with a recommendation. Answer in any order.", shot: { id: "discuss", title: "Discuss", alt: "A question about a webhook retry policy, with three choices and a recommendation, in the QualityLayer App" } },
  { id: "research", name: "Research", who: "agent", line: "Read the code first", text: "Agents trace how the code works today and what can be reused.", shot: { id: "research", title: "Research", alt: "Research on identity provisioning: a diagram of the existing services and a table of what the change can reuse" } },
  { id: "plan", name: "Plan", who: "you", line: "Approve it before any code", text: "Read the plan with its diagrams and designs. Comment on any part, then approve it.", shot: { id: "plan", title: "Plan", alt: "A complete plan for usage-based billing with a diagram, and Approve Plan in the task's header" } },
  { id: "outline", name: "Outline", who: "agent", line: "Split it into tasks", text: "Your agent splits the plan into tasks, each with a scenario that proves it works.", shot: { id: "outline", title: "Outline", alt: "A queue migration split into six slices in build order, with the scenarios that prove them" } },
  { id: "implement", name: "Implement", who: "agent", line: "Build it test first", text: "Work on separate files runs in parallel. Every test run is recorded.", shot: { id: "implement", title: "Implement", alt: "The billing build: slice 3 of 7 in progress, its tasks listed, finished slices marked done" } },
  { id: "verify", name: "Verify", who: "check", line: "Polish it, then check every point", text: "An agent that did not write the code polishes it, adds missing tests and checks every point of the plan. Risky changes get an independent review.", shot: { id: "verify", title: "Verify", alt: "Verification lanes for the billing change: polish, security, checks, an independent review and the outcome checks" } },
  { id: "review", name: "Review", who: "you", line: "Read the change and its proof", text: "See what changed, why, and the evidence for each agreed point. Approve, or ask for another pass.", shot: { id: "review", title: "Review", alt: "The finished billing change with what you asked for, what changed and how each point was checked" } },
  { id: "pull-request", name: "Pull request", who: "agent", line: "Follow it until it is merged", text: "Review threads and failing checks return to the task until the pull request merges.", shot: { id: "pull-request", title: "Pull request", alt: "An open pull request with its checks and review threads kept on the task" } },
];

const EXTRAS: Item[] = [
  { id: "memory", name: "Memory", icon: BookOpen, line: "Keep useful project lessons", text: "Claude Code and Codex reuse lessons between tasks. Share them per repository through Git; search or retire them in Settings.", shot: { id: "memory", title: "Project memory", alt: "The Memory tab with local lessons, per-project sharing and a searchable lesson browser; illustrative project data" }, link: { to: "/docs/memory", label: "Read about project memory" } },
  { id: "designs", name: "Design", icon: PenTool, line: "Comment on the spot", text: "Pin a comment anywhere on a design. Your agent replies in the thread and updates the design.", shot: { id: "design", title: "Design", alt: "A queue migration console open full size, with three numbered comment pins and the comments beside it" } },
  { id: "team", name: "Team", icon: Users, line: "Ask the people who know", text: "Teammates answer plan questions and review the finished change from their own App.", shot: { id: "team", title: "Team", alt: "The Team space with questions about shared plans, replies and the team's tasks" }, link: { to: "/pricing", label: "See the Team plan" } },
  { id: "cost", name: "Home", icon: House, line: "See what needs you", text: "What waits for you, what is running and what shipped, with each task's estimated cost.", shot: { id: "home", title: "Home", alt: "Home with tasks that need you, running work, agent cost estimates and shipped tasks" } },
  { id: "setup", name: "Settings", icon: SlidersHorizontal, line: "Pick your agents and models", text: "Choose the agent and model that plans, builds and checks, and whether tasks start as a product brief or a technical plan.", shot: { id: "setup", title: "Settings", alt: "Settings with the Product or Engineering level, the planning and building agents and models, and the review options" } },
];

const reducedMotion = () => typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
/** The header's height; on phones the step rail pins right under it. */
const HEADER = 60;

const src = (shot: Shot, theme: "light" | "dark") => `/product/${shot.id}-${theme}.webp`;
/** The App's own phone layout, captured at 390 px, so phones get a picture they can read. */
const phoneSrc = (shot: Shot, theme: "light" | "dark") => `/product/${shot.id}-phone-${theme}.webp`;
const PHONE = "(max-width: 640px)";

/** The desktop capture, or on a phone the phone capture. */
function Picture({ shot, theme, lazy = true }: { shot: Shot; theme: "light" | "dark"; lazy?: boolean }) {
  return (
    <picture>
      <source media={PHONE} srcSet={phoneSrc(shot, theme)} width={780} height={1400} />
      <img src={src(shot, theme)} alt={shot.alt} width="2880" height="1920" loading={lazy ? "lazy" : undefined} decoding="async" />
    </picture>
  );
}

function ImageDialog({ shot, theme, onClose, opener }: { shot: Shot; theme: "light" | "dark"; onClose: () => void; opener: HTMLElement | null }) {
  return (
    <Dialog open onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="ed-image-dialog" showCloseButton={false} onCloseAutoFocus={(event) => { event.preventDefault(); opener?.focus(); }}>
        <div className="ed-dialog-header">
          <DialogTitle>{shot.title}</DialogTitle>
          <DialogClose asChild><Button type="button" variant="outline" size="xl" aria-label="Close preview"><X size={18} aria-hidden="true" />Close</Button></DialogClose>
        </div>
        <Picture shot={shot} theme={theme} lazy={false} />
        <DialogDescription>{shot.id === "memory" ? "Illustrative projects in the Memory settings." : "Example task in the QualityLayer App."}</DialogDescription>
        <Button asChild variant="outline" size="xl"><a href={src(shot, theme)} target="_blank" rel="noopener noreferrer"><ExternalLink size={16} aria-hidden="true" />Open full-size image</a></Button>
      </DialogContent>
    </Dialog>
  );
}

/** The numbered steps in order, coloured by who acts; the line between them fills as the reader moves on. */
function Rail({ items, active, onPick }: { items: Item[]; active: number; onPick: (i: number) => void }) {
  return (
    <ol className="ed-rail" aria-label="The eight steps" style={{ "--done": active / (items.length - 1) } as CSSProperties}>
      {items.map((item, i) => (
        <li key={item.id}>
          <button type="button" className="ed-rail-step" data-who={item.who} data-state={i < active ? "done" : i === active ? "on" : "next"} aria-current={i === active ? "step" : undefined} aria-label={item.name} onClick={() => onPick(i)}>
            <span className="ed-num" aria-hidden="true">{i + 1}</span>
            <span className="ed-rail-name">{item.name}</span>
          </button>
        </li>
      ))}
    </ol>
  );
}

/**
 * One item in focus at a time. On wide screens the text scrolls on the left while the matching
 * screenshot stays pinned on the right and cross-fades; on tablets and phones each item carries its
 * own screenshot and, for the steps, the numbered rail pins under the header.
 */
function Scroller({ items, numbered, theme, onOpen }: { items: Item[]; numbered: boolean; theme: "light" | "dark"; onOpen: (shot: Shot, el: HTMLElement) => void }) {
  const narrow = useNarrow(1079);
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);

  const measure = useCallback(() => {
    const el = root.current;
    if (!el) return;
    const blocks = el.querySelectorAll<HTMLElement>(".ed-item");
    // The item nearest the reading line: the middle of the screen, or just under the pinned rail on phones.
    const line = narrow ? HEADER + window.innerHeight * 0.3 : window.innerHeight * 0.5;
    let best = 0, gap = Infinity;
    blocks.forEach((block, i) => {
      const r = block.getBoundingClientRect();
      const d = r.top <= line && r.bottom >= line ? 0 : Math.min(Math.abs(r.top - line), Math.abs(r.bottom - line));
      if (d < gap) { gap = d; best = i; }
    });
    setActive(best);
  }, [narrow]);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; measure(); }); };
    measure();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("scroll", onScroll); window.removeEventListener("resize", onScroll); };
  }, [measure]);

  const pick = (i: number) => {
    const block = root.current?.querySelectorAll<HTMLElement>(".ed-item")[i];
    if (!block) return;
    const r = block.getBoundingClientRect();
    const top = narrow ? r.top + window.scrollY - HEADER - 72 : r.top + window.scrollY - (window.innerHeight - r.height) / 2;
    window.scrollTo({ top, behavior: reducedMotion() ? "auto" : "smooth" });
  };

  const current = items[active];
  return (
    <div ref={root} className={`ed-scroll${numbered ? " numbered" : ""}`}>
      {numbered && narrow ? <div className="ed-rail-pin"><Rail items={items} active={active} onPick={pick} /></div> : null}
      <div className="ed-items">
        {items.map((item, i) => (
          <article key={item.id} id={item.id} className={`ed-item${i === active ? " on" : ""}`} data-who={item.who}>
            <h3>{numbered ? <span className="ed-num" aria-hidden="true">{i + 1}</span> : null}{item.icon ? <span className="mx-tile" aria-hidden="true"><item.icon size={18} strokeWidth={1.75} /></span> : null}{numbered ? <span className="w7-sr">Step {i + 1}: </span> : null}{item.name}</h3>
            <p className="ed-line">{item.line}</p>
            {narrow ? (
              <button type="button" className="ed-frame ed-inline" aria-label={`Enlarge ${item.shot.title}`} onClick={(event) => onOpen(item.shot, event.currentTarget)}>
                <Picture shot={item.shot} theme={theme} />
                <span className="ed-enlarge"><Expand size={14} aria-hidden="true" />Enlarge</span>
              </button>
            ) : null}
            <p className="ed-text">{item.text}</p>
            {numbered && item.who ? <p className="ed-who"><span className="ed-dot" aria-hidden="true" />{WHO[item.who]}</p> : null}
            {item.link ? <Link className="ed-link" to={item.link.to}>{item.link.label}</Link> : null}
          </article>
        ))}
      </div>
      {narrow ? null : (
        <div className="ed-stage">
          <div className="ed-pin">
            {numbered ? <Rail items={items} active={active} onPick={pick} /> : null}
            <button type="button" className="ed-frame" aria-label={`Enlarge ${current.shot.title}`} onClick={(event) => onOpen(current.shot, event.currentTarget)}>
              {items.map((item, i) => (
                <img key={item.id} className={i === active ? "on" : undefined} src={src(item.shot, theme)} alt={i === active ? item.shot.alt : ""} aria-hidden={i === active ? undefined : true} width="2880" height="1920" loading={i < 2 ? "eager" : "lazy"} decoding="async" />
              ))}
              <span className="ed-enlarge"><Expand size={14} aria-hidden="true" />Enlarge</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Editorial() {
  const { theme } = useTheme();
  const [shown, setShown] = useState<{ shot: Shot; opener: HTMLElement } | null>(null);
  const open = (shot: Shot, opener: HTMLElement) => setShown({ shot, opener });
  return (
    <>
      <section id="tour" className="ed-section mx-wrap" aria-labelledby="ed-workflow-h">
        <div className="ed-head">
          <h2 id="ed-workflow-h">From request to pull request in eight steps</h2>
          <p>You make the decisions; agents do the work and check it. Engineers start from a technical plan, product people from a product brief.</p>
          <ul className="ed-legend" aria-label="Colours">
            {(Object.keys(WHO) as Who[]).map((who) => <li key={who} data-who={who}><span className="ed-dot" aria-hidden="true" />{WHO[who]}</li>)}
          </ul>
        </div>
        <Scroller items={STEPS} numbered theme={theme} onOpen={open} />
        <div className="ed-outcome" id="films"><p>Every decision, document and test run stays with the change.</p><div><a href="/docs/">Read the workflow docs</a><a href={FILMS.overview.src} target="_blank" rel="noopener noreferrer">Watch the walkthrough</a></div></div>
      </section>
      <section className="ed-section mx-wrap" aria-labelledby="ed-context-h">
        <div className="ed-head"><h2 id="ed-context-h">Also in the App</h2><p>Available on every task.</p></div>
        <Scroller items={EXTRAS} numbered={false} theme={theme} onOpen={open} />
      </section>
      {shown ? <ImageDialog shot={shown.shot} theme={theme} opener={shown.opener} onClose={() => setShown(null)} /> : null}
    </>
  );
}
