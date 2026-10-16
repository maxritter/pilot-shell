/**
 * The website's questions and answers. Each answer must hold for the product as it
 * ships; when the product changes, change it here. Plain text only: the home page's
 * structured data reuses these answers. Words follow the App's glossary: Your turn, passed,
 * Checked by agents, Found while checking, Only you can confirm, Questions for you.
 */

import { PLANS } from "./pricing";

export type Faq = { question: string; answer: string };

const faq = (question: string, answer: string): Faq => ({ question, answer });

/** Monthly and yearly prices of a plan, read from the plans themselves so the answer below never drifts. */
const priced = (id: "solo" | "team") => {
  const price = PLANS.find((p) => p.id === id)?.price;
  if (price === undefined || price === "Custom") throw new Error(`${id} has no price`);
  return { ...price, year: price.yearly * 12 };
};
const solo = priced("solo");
const team = priced("team");

export const FAQS: Faq[] = [
  faq(
    "Can I use it on my own, or only with a team?",
    "On your own. One developer runs all eight steps. The Team plan adds questions to teammates, Slack messages and reviewing a change together.",
  ),
  faq(
    "How is this different from plan mode?",
    "Spec-driven development starts with an approved plan. Here, questions arrive as a batch in Your turn; answer in any order, and each answer reaches your agent immediately. You comment on one plan with diagrams and designs, and approve it before coding. Your agent builds it test first, another agent polishes and tests it, and risky changes get independent AI code review.",
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
    "Can I run my agent in the App?",
    "Yes. Start Claude Code, Codex, Pi or OpenCode from New task or Implement and type in its interactive window. You can also keep your terminal.",
  ),
  faq(
    "What does it cost to run?",
    "Your agents run on your own subscription. The App shows each step's estimated cost.",
  ),
  faq(
    "Does my code leave my computer?",
    "Your coding agent sends code to its provider under your existing data settings. QualityLayer keeps plans, designs and agent output on your computer. Sharing sends the task and its progress, encrypted on your machine, with designs only if you include them; never repository code or terminal output. A screenshot you attach to a feedback report can show code, so check it first.",
  ),
  faq(
    "I use Pilot Shell today. What happens?",
    "The App replaces Pilot Shell on first start, without questions. Your licence carries over, Pilot Shell's tools and memories stay, and your agent can remove what you no longer need.",
  ),
];

export const PRICING_FAQS: Faq[] = [
  faq(
    "How long is the trial?",
    "Seven days from your first run, with everything in Solo. Sharing with a team needs the Team plan. After the trial, choose a plan to continue.",
  ),
  faq(
    "Monthly or yearly?",
    `Yearly saves 20%. Solo is $${solo.yearly} a month, billed as $${solo.year} a year, instead of $${solo.monthly} a month. Team is $${team.yearly} per seat a month, billed as $${team.year} a year, instead of $${team.monthly}.`,
  ),
  faq(
    "Do I pay for AI usage here?",
    "No. Claude Code, Codex, Pi and OpenCode use your own subscriptions or API accounts. QualityLayer charges only for itself.",
  ),
  faq(
    "Is there a limit on tasks or repositories?",
    "No. Each plan is per developer, with unlimited tasks, repositories and agents.",
  ),
  faq(
    "Which agents does it work with?",
    "Claude Code, Codex, Pi and OpenCode have native setup, model choices and interactive sessions in the App. Choose any installed agent for a separate review. Other agents that run shell commands can follow the same workflow from your terminal.",
  ),
  faq(
    "Who needs a seat?",
    "Everyone on your team who uses QualityLayer. Outside people you invite to comment through a link do not.",
  ),
  faq(
    "Does my code leave my computer?",
    "Plans are files in your repository, and the App runs on your computer. Your AI agent keeps its own provider and data settings. A shared plan is encrypted on your machine first, so we store it but can’t read it. We see who shared it, which task, when and its step. A screenshot you attach to a feedback report can show code, so check it first.",
  ),
  faq(
    "What does Enterprise include?",
    "For companies with 20 developers or more. It can include hosting in your own cloud or on-premise, volume pricing, single sign-on, invoicing and custom terms. Write to us and we scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "The App or Pilot Shell’s own updater moves you over, without questions. Your plans, Pilot Shell's tools and its memories stay; your agent can remove what you no longer need. A paid licence keeps today's price. Without one, your 7-day trial starts.",
  ),
];
