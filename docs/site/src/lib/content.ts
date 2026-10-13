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
    "On your own. One developer can run all eight steps, from Discuss to the pull request. A Team plan adds questions to teammates, Slack messages and reviewing a change together.",
  ),
  faq(
    "How is this different from plan mode?",
    "Plan mode gives you a plan in the chat. In QualityLayer, questions arrive together as a batch in Your turn; answer in any order, and each answer reaches your agent immediately. You then read one plan with diagrams and designs to comment on, and approve it before any code is written. Your agent builds it test first, an agent that did not write the code polishes and tests it, and a risky change gets its independent review.",
  ),
  faq(
    "What about small changes and bugs?",
    "QualityLayer is for medium and large changes. When a request is too small for it, the agent writes a prompt for your plain agent and offers to run it. A bug takes the same steps, starting with its cause.",
  ),
  faq(
    "Is it for product managers as well as engineers?",
    "Yes. Choose Product or Engineering at Setup, and change it any time in Settings › Workflow. With Product, a task starts as a product brief: Discuss settles the problem, how success is measured and the first release, and the plan reads in product words with the engineering detail folded away. With Engineering, a task starts with the full technical plan. The task header shows each task's level and switches it for that one task.",
  ),
  faq(
    "Can I run my agent in the App?",
    "The unreleased App-run candidate lets you start Claude Code or Codex from New task or Implement, type in its own interactive window, and fold it while work continues. Your terminal remains an option. Windows App runs are planned for later. This candidate is being verified locally and is not available as a public release yet.",
  ),
  faq(
    "What does it cost to run?",
    "Your agents’ own usage, on your subscription. The App shows the estimated cost of each step.",
  ),
  faq(
    "Does my code leave my computer?",
    "Your coding agent sends code to its provider under your existing data settings. QualityLayer keeps your plans, designs and agent output on your computer. Sharing sends the task and its progress, encrypted on your machine, with designs only when you include them; it does not send repository code or terminal output. A screenshot you attach to a feedback report can show code, so check it before sending.",
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
    "Claude Code and Codex, in the terminal, their desktop apps or your IDE; the App sets both up for you. For another coding agent, the App copies a prompt you can hand it. With both Claude Code and Codex installed, the other agent also reviews your plan and any risky change.",
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
    "Enterprise is for companies with 20 developers or more. It can include hosting in your own cloud or on-premise, volume pricing, single sign-on, invoicing and custom terms. Write to us and we will scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "The App replaces Pilot Shell on first start, and Pilot Shell’s own updater moves you over too. It asks nothing: the tools Pilot Shell installed and its memories stay, and your agent can remove what you no longer need. Your plans carry over, and a paid licence keeps working at the price you pay today. Without one, your 7-day trial starts.",
  ),
];
