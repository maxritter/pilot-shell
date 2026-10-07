/**
 * Plans as sold today: the live Polar checkouts and their prices. These are the
 * values that charge customers, so a price change happens here and in Polar together.
 * Enterprise has no checkout: it is built with a company that asks for it.
 */
import { CONTACT_EMAIL } from "./product";

/** The four colours a highlight or a table group can carry, one per part of the workflow. */
export type Hue = "plan" | "build" | "verify" | "review";

export interface Plan {
  id: "solo" | "team" | "enterprise";
  name: string;
  audience: string;
  /** US dollars per month (per seat for Team): billed monthly, and billed yearly at 20% off. "Custom" for Enterprise. */
  price: { monthly: number; yearly: number } | "Custom";
  per: string;
  cta: string;
  /** The Polar checkout for each billing period; Enterprise has one mail link. */
  href: { monthly: string; yearly: string } | string;
  featured: boolean;
  badge?: string;
  plus: string;
  /** Four short highlights per plan, of about the same length; the table holds the detail. */
  highlights: [Hue, string][];
}

export const PLANS: Plan[] = [
  {
    id: "solo",
    name: "Solo",
    audience: "For one developer.",
    price: { monthly: 20, yearly: 16 },
    per: "per month",
    cta: "Start Solo",
    href: {
      monthly: import.meta.env.VITE_POLAR_CHECKOUT_SOLO_MONTHLY || "https://buy.polar.sh/polar_cl_7qzxxKiqZXIFe3Uabodh7IauA937iVROT5qVW4VyuUf",
      yearly: import.meta.env.VITE_POLAR_CHECKOUT_SOLO_YEARLY || "https://buy.polar.sh/polar_cl_9krLYPvWYMBAXX4nL4LolXKgB5cAEA7J57H8Y3j0oQY",
    },
    featured: false,
    plus: "Everything one developer needs:",
    highlights: [
      ["plan", "Approve the plan before any code is written"],
      ["build", "Built test first, every test run recorded"],
      ["verify", "Checked against your request before you see it"],
      ["review", "Works inside Claude Code and Codex"],
    ],
  },
  {
    id: "team",
    name: "Team",
    audience: "For teams, per seat.",
    price: { monthly: 40, yearly: 32 },
    per: "per seat / month",
    cta: "Start Team",
    href: {
      monthly: import.meta.env.VITE_POLAR_CHECKOUT_TEAM_MONTHLY || "https://buy.polar.sh/polar_cl_Qeegkxuq603Ai4UAWSTCT7rOqLmKACxgmKbw40AAj5b",
      yearly: import.meta.env.VITE_POLAR_CHECKOUT_TEAM_YEARLY || "https://buy.polar.sh/polar_cl_vDV57vWuG7nb2SCgK9RZUzunpOJo9pfjCELnc1PxhTh",
    },
    featured: true,
    badge: "For teams",
    plus: "Everything in Solo, plus:",
    highlights: [
      ["plan", "Share plans and collect your team’s feedback"],
      ["build", "See every shared task and how far it is"],
      ["verify", "Invite people outside your team to comment"],
      ["review", "Review finished changes together"],
    ],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    audience: "For 20 developers or more.",
    price: "Custom",
    per: "volume pricing",
    cta: "Contact us",
    href: `mailto:${CONTACT_EMAIL}?subject=QualityLayer%20Enterprise`,
    featured: false,
    badge: "On request",
    plus: "Everything in Team, plus:",
    highlights: [
      ["plan", "Host it in your own cloud or on-premise"],
      ["build", "Volume pricing for many seats"],
      ["verify", "Single sign-on"],
      ["review", "Invoicing and custom terms"],
    ],
  },
];

/** A cell: included, not included, or available when a company asks for it. */
export type Cell = boolean | "request";
export type CompareRow = { feature: string; solo: Cell; team: Cell; enterprise: Cell; note?: string };
export type CompareGroup = { name: string; hue: Hue; rows: CompareRow[] };

/** Enterprise has everything Team has unless a row says otherwise. */
const row = (feature: string, solo: Cell, team: Cell, note?: string, enterprise: Cell = team): CompareRow => ({
  feature,
  solo,
  team,
  enterprise,
  note,
});
const onRequest = (feature: string) => row(feature, false, false, undefined, "request");

export const COMPARE: CompareGroup[] = [
  {
    name: "Plan",
    hue: "plan",
    rows: [
      row("Approve one plan before any code is written", true, true),
      row("Answer questions in batches, in any order", true, true, "Each answer reaches your agent immediately in Your turn"),
      row("Agree to each Done means point separately", true, true, "A changed point returns with its old and new words"),
      row("Decisions shown as diagrams and a clickable mockup", true, true),
      row("Read the full-size Plan with line comments", true, true),
      row("Bugs start with finding their cause", true, true),
      row("A ready prompt for requests too small for a plan", true, true, "Your plain agent runs it"),
      row("Copy the plan as a PRD", true, true, "For Confluence, Google Docs or Jira"),
    ],
  },
  {
    name: "Build",
    hue: "build",
    rows: [
      row("Choose the models of the agents that build and check", true, true),
      row("Every task test first, every test run recorded", true, true),
      row("Slices that don’t overlap build side by side", true, true),
      row("The cost of every step", true, true, "Estimated at list price"),
    ],
  },
  {
    name: "Verify",
    hue: "verify",
    rows: [
      row("Polish and security review before the final check", true, true, "Security runs when the change touches outside input, sign-in or secrets"),
      row("Checked by agents that did not write the code", true, true, "Every check against what you asked for"),
      row("The other coding agent reviews risky plans too", true, true, "Runs by itself; needs Claude Code and Codex"),
    ],
  },
  {
    name: "Review",
    hue: "review",
    rows: [
      row("Approve the finished change, with its evidence", true, true, "Only you can confirm shows what no agent may check"),
      row("Review finished changes as a team", false, true, "The code itself is reviewed in your pull request"),
    ],
  },
  {
    name: "Everyday",
    hue: "build",
    rows: [
      row("The App for macOS, Windows and Linux", true, true, "On a server or in WSL, it opens in your browser"),
      row("A notification when it is Your turn", true, true, "In the App's bell, from the menu bar, and in Claude Code above the prompt"),
      row("Live agent status and shipped tasks on Home", true, true, "Time, estimated cost and tasks in each step"),
      row("Your AI agents can message each other", true, true, "Claude Code and Codex sessions on your computer"),
    ],
  },
  {
    name: "Team",
    hue: "build",
    rows: [
      row("Share plans with your team", false, true),
      row("Team feedback goes straight to your agent", false, true),
      row("Ask a teammate about any part of a plan", false, true, "They get a Slack message that opens the question under Questions for you"),
      row("Teammates answer with their own agent", false, true, "Their agent drafts the answer; nothing is sent without their yes"),
      row("See every shared task and how far it is", false, true),
      row("Invite people outside your team to comment", false, true),
      row(
        "Plans, comments and links are encrypted on your machine",
        false,
        true,
        "We can’t read them. We see who shared, who was asked, which task, when and its step. The guest page’s code comes from us. If you connect Slack, the task title and question pass through our server to Slack, and wait a day at most if Slack is busy.",
      ),
      row("Manage seats and billing in one place", false, true),
    ],
  },
  {
    name: "Enterprise",
    hue: "review",
    rows: [
      onRequest("Host it in your own cloud, on-premise or in a private VPC"),
      onRequest("Volume pricing"),
      onRequest("Single sign-on (SSO)"),
      onRequest("Custom terms and invoicing"),
    ],
  },
];

/** The overlay checkout is loaded in production only; elsewhere the link opens Polar in a new tab. */
export const USE_EMBED_CHECKOUT =
  import.meta.env.PROD && !import.meta.env.VITE_POLAR_PORTAL_URL?.includes("sandbox");
