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
  /** A number of US dollars, or "Custom" for Enterprise. */
  price: number | "Custom";
  per: string;
  cta: string;
  href: string;
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
    price: 14,
    per: "per month",
    cta: "Buy Solo",
    href:
      import.meta.env.VITE_POLAR_CHECKOUT_SOLO ||
      "https://buy.polar.sh/polar_cl_nxoqkuI0m3K60V4EpyaruDdPsd7CjS4jalKqc4TszL3",
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
    price: 35,
    per: "per seat, per month",
    cta: "Buy Team",
    href:
      import.meta.env.VITE_POLAR_CHECKOUT_TEAM ||
      "https://buy.polar.sh/polar_cl_y5uSffkVLnESyfzfOSJ1M9YmMd8sIpcT7bza82oFv4C",
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
    audience: "For companies, built with you.",
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
      ["verify", "Advanced metrics across your teams"],
      ["review", "Single sign-on and custom terms"],
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
      row("Decisions shown as diagrams and a clickable mockup", true, true),
      row("Bugs start with finding their cause", true, true),
      row("A ready prompt for requests too small for a plan", true, true, "Your plain agent runs it"),
      row("Copy the plan as a PRD", true, true, "For Confluence, Google Docs or Jira"),
    ],
  },
  {
    name: "Build",
    hue: "build",
    rows: [
      row("Choose the models that build and check", true, true),
      row("Every task test first, every test run recorded", true, true),
      row("Slices that don’t overlap build side by side", true, true),
      row("Tokens and estimated cost for every step", true, true, "With a warning before a task passes your budget"),
    ],
  },
  {
    name: "Verify",
    hue: "verify",
    rows: [
      row("Polish and security review before the final check", true, true, "Security runs when the change touches outside input, sign-in or secrets"),
      row("An independent check against what you asked for", true, true, "By an AI that did not write the code"),
      row("A second opinion from another vendor’s AI", true, true, "Off by default; needs Claude Code and Codex"),
    ],
  },
  {
    name: "Review",
    hue: "review",
    rows: [
      row("Approve the finished change, with its evidence", true, true),
      row("Review finished changes as a team", false, true, "The code itself is reviewed in your pull request"),
    ],
  },
  {
    name: "Everyday",
    hue: "build",
    rows: [
      row("The App for macOS, Windows and Linux", true, true, "On a server or in WSL, it opens in your browser"),
      row("A notification when something needs you", true, true, "From the menu bar, and in Claude Code above the prompt"),
      row("Your AI agents can message each other", true, true, "Claude Code and Codex sessions on your computer"),
    ],
  },
  {
    name: "Team",
    hue: "build",
    rows: [
      row("Share plans with your team", false, true),
      row("Team feedback goes straight to your agent", false, true),
      row("Ask a teammate about any part of a plan", false, true, "They get a Slack message that opens the question in their App"),
      row("Teammates answer with their own agent", false, true, "Claude Code, Codex or Grok Bot drafts; nothing is sent without their yes"),
      row("See every shared task and how far it is", false, true),
      row("Invite people outside your team to comment", false, true),
      row(
        "Plans, comments and links are encrypted on your machine",
        false,
        true,
        "We can’t read them. We see who shared, who was asked, which task, when and its stage. The guest page’s code comes from us. If you connect Slack, a nudge’s task title and question pass through our server to Slack, and wait a day at most if Slack is busy.",
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
      onRequest("Advanced metrics across teams and projects"),
      onRequest("Single sign-on (SSO)"),
      onRequest("Custom terms and invoicing"),
    ],
  },
];

/** The overlay checkout is loaded in production only; elsewhere the link opens Polar in a new tab. */
export const USE_EMBED_CHECKOUT =
  import.meta.env.PROD && !import.meta.env.VITE_POLAR_PORTAL_URL?.includes("sandbox");
