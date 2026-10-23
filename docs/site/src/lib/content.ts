/**
 * The website's questions and answers. Each answer must hold for the product as it
 * ships; when the product changes, change it here. Plain text only: the home page's
 * structured data reuses these answers. Words follow the App's glossary: Your turn, passed,
 * Checked by agents, Found while checking, Only you can confirm, Questions for you.
 */

import { PLANS, formatPrice } from "./pricing";

export type Faq = { question: string; answer: string };

const faq = (question: string, answer: string): Faq => ({ question, answer });

/** Monthly and yearly prices of a plan, read from the plans themselves so the answer below never drifts. */
const priced = (id: "solo" | "team") => {
  const price = PLANS.find((p) => p.id === id)?.price;
  if (price === undefined || price === "Custom") throw new Error(`${id} has no price`);
  return { monthly: formatPrice(price.monthly), yearly: formatPrice(price.yearly / 12), year: formatPrice(price.yearly) };
};
const solo = priced("solo");
const team = priced("team");

export const FAQS: Faq[] = [
  faq(
    "Can I use the models and subscriptions I already have?",
    "Yes. Claude Code, Codex, Cursor, Grok, Antigravity, Pi and OpenCode run on the login or API key you already have, with the models your plan offers. QualityLayer charges only for itself, never for AI usage, and the App shows each step's estimated cost.",
  ),
  faq(
    "How is this different from plan mode?",
    "Spec-driven development starts with an approved plan. Here, questions arrive as a batch in Your turn; answer in any order, and each answer reaches your agent immediately. You comment on one plan with diagrams and artifacts, and approve it before coding. Your agent builds it test first, another agent polishes and tests it, and risky changes get independent AI code review.",
  ),
  faq(
    "What about small changes and bugs?",
    "QualityLayer is for medium and large changes. For a small one, the agent writes a prompt for your plain agent and offers to run it. Bugs take the same steps, starting with the cause.",
  ),
  faq(
    "Is it for product managers as well as engineers?",
    "Yes. Choose Product or Engineering at Setup or in Settings › Workflow. Product starts with a brief: the problem, how success is measured and the first release, with engineering detail folded away. Engineering starts with the full technical plan. The task header switches the level for one task.",
  ),
  faq(
    "Can I run my agent in the App or browser?",
    "Yes. Start Claude Code, Codex, Cursor, Grok, Antigravity, Pi or OpenCode from New task or Implement. Your task stays on the left and the agent runs in the right sidebar. Use the desktop App or the browser connected to your local installation. Your own terminal, VS Code and other IDEs remain available.",
  ),
  faq(
    "Can I use it on my own, or only with a team?",
    "On your own. One developer runs all seven steps. The Team plan adds questions to teammates, Slack messages and reviewing a change together.",
  ),
  faq(
    "Can I see how much of my plan is left?",
    "For Claude Code and Codex, yes. The sidebar shows the window with the least left, the conversation footer warns when one runs low, and Settings › Usage lists every window with its reset time. The other agents report no limits, and the App says so. A build that stops on a limit can continue by itself when the window resets.",
  ),
  faq(
    "Does my code leave my computer?",
    "Your coding agent sends code to its provider under your existing data settings. QualityLayer keeps plans, artifacts and agent output on your computer. Sharing sends the task and its progress, encrypted on your machine, with artifacts only if you include them; never terminal output or the repository's code. Review code travels between your computer and your own Git remote. QualityLayer stores your team's encrypted comments, the short lines of code they quote and the commits they point to. A screenshot you attach to a feedback report can show code, so check it first.",
  ),
  faq(
    "I use Pilot Shell today. What happens?",
    "Keep using Pilot Shell 11 for as long as you want, including alongside QualityLayer. Setup leaves Pilot Shell and its tools in place. Your paid licence carries over; import memories per project in Settings → Memory.",
  ),
];

export const PRICING_FAQS: Faq[] = [
  faq(
    "How long is the trial?",
    "Seven days from your first run, with everything in Solo. Sharing with a team needs the Team plan. After the trial, choose a plan to continue.",
  ),
  faq(
    "Monthly or yearly?",
    `Solo costs ${solo.year} a year, equivalent to ${solo.yearly} a month, instead of ${solo.monthly} billed monthly. Team costs ${team.year} per seat a year, equivalent to ${team.yearly} per seat a month, instead of ${team.monthly} billed monthly.`,
  ),
  faq(
    "Do I pay for AI usage here?",
    "No. Your coding agents use your own subscriptions or API accounts. QualityLayer charges only for itself.",
  ),
  faq(
    "Is there a limit on tasks or repositories?",
    "No. Each plan is per developer, with unlimited tasks, repositories and agents.",
  ),
  faq(
    "Which agents does it work with?",
    "Claude Code, Codex, Cursor, Grok, Antigravity, Pi and OpenCode have native setup, model choices and interactive sessions in the App or browser. Choose any installed agent for a separate review. The CLI connects other agents that run shell commands, including in your own terminal, VS Code or another IDE.",
  ),
  faq(
    "Who needs a seat?",
    "Everyone on your team who uses QualityLayer. Outside people you invite to comment through a link do not.",
  ),
  faq(
    "Does my code leave my computer?",
    "Plans are files in your repository, and the App runs on your computer. Your AI agent keeps its own provider and data settings. A shared plan is encrypted on your machine first, so we store it but can’t read it. We see who shared it, which task, when and its step. Review code travels between your computer and your own Git remote. QualityLayer stores your team's encrypted comments, the short lines of code they quote and the commits they point to. A screenshot you attach to a feedback report can show code, so check it first.",
  ),
  faq(
    "What does Enterprise include?",
    "For companies with 20 developers or more. It can include hosting in your own cloud or on-premise, volume pricing, single sign-on, invoicing and custom terms. Write to us and we scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "You can use Pilot Shell 11 and QualityLayer in parallel. QualityLayer leaves Pilot Shell, its tools and its configuration in place. Your paid subscription keeps its existing price while it stays active. If it ends, a new subscription uses current prices. Without an active licence, you get a fresh seven-day trial. Import memories per project in Settings → Memory.",
  ),
];
