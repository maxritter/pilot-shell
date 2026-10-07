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
    "Does it replace my coding agent?",
    "No. Claude Code or Codex still writes the code, with the subscription you already have. QualityLayer adds the plan you approve, the tests, the checks by agents that did not write the code, and the App that shows what each decision is about.",
  ),
  faq(
    "Can I use it on my own, or only with a team?",
    "On your own. One developer goes through every step: Discuss, Plan, Implement, Verify and Review. A Team plan adds questions to teammates, Slack messages, and reviewing a change together.",
  ),
  faq(
    "How is this different from plan mode?",
    "Plan mode gives you a plan in the chat. QualityLayer gives you one plan with diagrams and a design to comment on. Independent questions come in batches in Your turn. Answer in any order; each answer reaches your agent immediately, while it keeps working on the rest. It builds the plan test first, and agents that did not write the code check the result.",
  ),
  faq(
    "What about small changes and bugs?",
    "QualityLayer is for medium and large changes. When a request is too small for it, the agent writes a prompt for your plain agent and offers to run it. A bug takes the same steps, starting with its cause.",
  ),
  faq(
    "What does it cost to run?",
    "Your agents’ own usage, on your subscription. The App shows the estimated cost of each step.",
  ),
  faq(
    "Does my code leave my computer?",
    "Your coding agent sends code to its provider under your existing data settings. QualityLayer keeps your plans and designs on your computer. Sharing sends the plan and its progress, encrypted on your machine; it does not send your code or the design page. A screenshot you attach to a feedback report can show code, so check it before sending.",
  ),
  faq(
    "What does Send feedback share?",
    "A report goes to QualityLayer as a private issue, with your text and the screenshots you add. Diagnostics are on by default, and you see them before you send. They name the versions of the App, the command line, Claude Code and Codex, your system and its architecture, the kind of page you were on and your licence. They also count the errors of the last hour by kind. They never include your code, the text of a plan or document, task titles, repository or branch names, or file paths. Screenshots can show code or plans.",
  ),
  faq(
    "Which agents work with it?",
    "Claude Code and Codex, in the terminal, their desktop apps or your IDE. For another coding agent, the App copies a prompt you can hand it.",
  ),
  faq(
    "I use Pilot Shell today. What happens?",
    "The App replaces Pilot Shell on first start, and your licence carries over. It asks nothing: the tools Pilot Shell installed and its memories stay, and your agent can remove what you no longer need.",
  ),
];

export const PRICING_FAQS: Faq[] = [
  faq(
    "How long is the trial?",
    "Seven days, starting the first time you run QualityLayer, with everything in Solo. Sharing with a team needs a Team plan. After the trial, choose a plan to keep going.",
  ),
  faq(
    "Monthly or yearly?",
    `Yearly saves 20%. Solo is $${solo.yearly} a month, billed as $${solo.year} a year, instead of $${solo.monthly} a month. Team is $${team.yearly} per seat a month, billed as $${team.year} a year, instead of $${team.monthly}.`,
  ),
  faq(
    "Do I pay for AI usage here?",
    "No. Your agents run on your own Claude Code or Codex plan, as they do today. QualityLayer charges only for itself.",
  ),
  faq(
    "Is there a limit on tasks or repositories?",
    "No. Each plan is per developer, for as many tasks, repositories and agents as you use.",
  ),
  faq(
    "Which agents does it work with?",
    "Claude Code and Codex, in the terminal, their desktop apps or your IDE; the App sets both up for you. For another coding agent, the App copies a prompt you can hand it. On a risky plan, the other coding agent reviews it too, which needs both Claude Code and Codex.",
  ),
  faq(
    "Who needs a seat?",
    "Each person on your team who uses QualityLayer. People outside your team whom you invite to comment through a link do not need one.",
  ),
  faq(
    "Does my code leave my computer?",
    "Plans are files in your repository, and the QualityLayer App runs on your computer. Your AI agent keeps its own provider and data settings. When you share a task, its plan is encrypted on your machine first, so we store it but can’t read it. We see who shared it, which task, when and its step. A screenshot you attach to a feedback report can show code, so attach only what you are happy to send.",
  ),
  faq(
    "What does Enterprise include?",
    "Enterprise is built with you when your company asks for it, for 20 developers or more: hosting in your own cloud or on-premise, volume pricing, single sign-on, invoicing and custom terms. Write to us and we will scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "The App replaces Pilot Shell on first start, and Pilot Shell’s own updater moves you over too. It asks nothing: the tools Pilot Shell installed and its memories stay, and your agent can remove what you no longer need. Your plans carry over, and a paid licence keeps working at the price you pay today. Without one, your 7-day trial starts.",
  ),
];
