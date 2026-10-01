import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

/** A route in the embedded Cockpit demo (qualitylayer/src/ui/demo), as its hash router knows it. */
export type DemoRoute =
  | { view: "home" }
  | { view: "settings"; tab?: string }
  | { view: "task"; id: string; doc: string | null }
  | { view: "team-task"; id: string; doc: string | null };

export type Who = "you" | "agent";
/** One moment of a stop: where the demo goes, what it shows, and what to try there. */
export type Moment = { label?: string; who?: Who; route: DemoRoute; context: string; hint: string };
export type Stop = { id: string; label: string; who?: Who; side?: boolean; moments: Moment[] };

const task = (id: string, doc: string | null): DemoRoute => ({ view: "task", id, doc });

/**
 * The tour: your queue and the team at the ends, Settings last, and one stop per stage between.
 * A stage with two moments (the agent writing, then your review) carries both.
 */
export const STOPS: Stop[] = [
  { id: "queue", label: "Your queue", side: true, moments: [
    { route: { view: "home" }, context: "Every task, sorted by who has to act next.", hint: "Open Queue migration, or search for “webhook”." }] },
  { id: "frame", label: "Frame", who: "you", moments: [
    { route: task("reindex", "README.md"), context: "The agent reads your code, then agrees with you what done means.", hint: "Its open question waits in your agent’s chat. Your answers fill in this page." }] },
  { id: "research", label: "Research", who: "you", moments: [
    { label: "Agent writing", who: "agent", route: task("research", "01-research.md"), context: "Helper agents are still reading the code. You can already read and comment.", hint: "Open the “being written” label to see what is still missing." },
    { label: "Your review", who: "you", route: task("queue", "01-research.md"), context: "What the code does today, written once for you and once for the agent.", hint: "Switch between For you and For the agent at the top." }] },
  { id: "design", label: "Design", who: "you", moments: [
    { route: task("queue", "02-design.md"), context: "Diagrams and mockups first, your decisions at the end.", hint: "Press + beside a passage to comment, then approve or ask for changes." }] },
  { id: "outline", label: "Outline", who: "you", moments: [
    { route: task("invoice", "03-outline.md"), context: "The work, split into small slices that are each tested.", hint: "See how the fix is split, and where the build tests itself." }] },
  { id: "build", label: "Build", who: "agent", moments: [
    { label: "Handoff", who: "you", route: task("invoice", "handoff"), context: "The plan is approved and saved. You choose which agent builds it.", hint: "Pick an agent, and the prompt to start it follows." },
    { label: "Building", who: "agent", route: task("tokens", "checkpoint"), context: "Slices build side by side and test themselves.", hint: "Open Webhook retries: a test failed three times, so it asks you." }] },
  { id: "verify", label: "Verify", who: "agent", moments: [
    { route: task("export", "verify"), context: "An AI that did not write the code checks it against your request, with evidence.", hint: "Open SSO group sync to see a build that stopped after three failed checks." }] },
  { id: "review", label: "Review", who: "you", moments: [
    { route: task("export", "changes"), context: "Your team reviews the finished change: what it proves, the evidence, the code.", hint: "Open Dana’s comment, filter the conversation, or copy the command for your agent." }] },
  { id: "team", label: "Team", side: true, moments: [
    { route: { view: "team-task", id: "billing", doc: "02-design.md" }, context: "Anna’s design, with comments and approvals from Ben, Chen, Dana and you.", hint: "Select a passage to comment, or open Chen’s task from the team list." }] },
  { id: "settings", label: "Settings", side: true, moments: [
    { route: { view: "settings", tab: "workflow" }, context: "Choose which model does which job, and turn jobs on or off.", hint: "Pick a model for a job, or turn the job off." }] },
];

/** The same place, ignoring a settings tab and a scroll anchor. */
export function sameRoute(a: DemoRoute, b: DemoRoute): boolean {
  if (a.view !== b.view) return false;
  if (a.view === "task" || a.view === "team-task") {
    const other = b as typeof a;
    return a.id === other.id && a.doc === other.doc;
  }
  return true;
}

function locate(route: DemoRoute): [number, number] | null {
  for (let i = 0; i < STOPS.length; i++) {
    const j = STOPS[i].moments.findIndex((m) => sameRoute(m.route, route));
    if (j >= 0) return [i, j];
  }
  return null;
}

/** A target from elsewhere on the page: a stop ("design"), a stop and moment ("build:0"), or a route. */
export type Target = string | DemoRoute;

type Tour = {
  stop: number;
  moment: number;
  exploring: boolean;
  /** The route the demo should show, and a counter that changes on every request so a repeat still navigates. */
  route: DemoRoute;
  revision: number;
  select: (stop: number, moment?: number, scroll?: boolean) => void;
  go: (target: Target) => void;
  observe: (route: DemoRoute) => void;
};

const Context = createContext<Tour | null>(null);

function scrollToDemo() {
  const el = document.getElementById("cockpit");
  if (!el) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 60, behavior: reduce ? "instant" : "smooth" });
}

const START = STOPS.findIndex((s) => s.id === "design");

export function DemoTourProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState({ stop: START, moment: 0, exploring: false, direct: null as DemoRoute | null, revision: 0 });

  const select = useCallback((stop: number, moment = 0, scroll = false) => {
    setState((s) => ({ stop, moment, exploring: false, direct: null, revision: s.revision + 1 }));
    if (scroll) scrollToDemo();
  }, []);

  const go = useCallback((target: Target) => {
    if (typeof target === "string") {
      const [id, j] = target.split(":");
      const i = STOPS.findIndex((s) => s.id === id);
      if (i < 0) return;
      select(i, j === undefined ? STOPS[i].moments.length - 1 : Number(j), true);
      return;
    }
    const at = locate(target);
    setState((s) => (at ? { stop: at[0], moment: at[1], exploring: false, direct: null, revision: s.revision + 1 }
      : { ...s, exploring: true, direct: target, revision: s.revision + 1 }));
    scrollToDemo();
  }, [select]);

  // The demo reports where the visitor went; the tour follows, or says they are exploring.
  const observe = useCallback((route: DemoRoute) => {
    const at = locate(route);
    setState((s) => {
      if (at) return at[0] === s.stop && at[1] === s.moment && !s.exploring ? s : { ...s, stop: at[0], moment: at[1], exploring: false, direct: null };
      return s.exploring ? s : { ...s, exploring: true };
    });
  }, []);

  const value = useMemo<Tour>(() => ({
    stop: state.stop,
    moment: state.moment,
    exploring: state.exploring,
    route: state.direct ?? STOPS[state.stop].moments[state.moment]?.route ?? STOPS[state.stop].moments[0].route,
    revision: state.revision,
    select,
    go,
    observe,
  }), [state, select, go, observe]);

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useDemoTour(): Tour {
  const tour = useContext(Context);
  if (!tour) throw new Error("The Cockpit tour needs its provider");
  return tour;
}
