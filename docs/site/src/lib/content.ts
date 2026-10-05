/**
 * The website's questions and answers. Each answer must hold for the product as it
 * ships; when the product changes, change it here. Plain text only: the home page's
 * structured data reuses these answers. Words follow the App's glossary: Needs you, passed,
 * Checked by agents, Found while checking, Only you can confirm, Questions for you.
 */

export type Faq = { question: string; answer: string };

const faq = (question: string, answer: string): Faq => ({ question, answer });

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
    "Plan mode gives you a plan in the chat. QualityLayer gives you one plan with diagrams and a mockup to comment on. Your agent asks you each decision in the chat, one at a time. It builds the plan test first, and agents that did not write the code check the result.",
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
    "No. Plans are files in your repository, and the App runs on your computer. Sharing with your team sends the plan and its progress, encrypted on your machine, never your code. The one way it can leave is a screenshot you attach to a feedback report, if the screenshot shows it.",
  ),
  faq(
    "What does Send feedback share?",
    "A report goes to QualityLayer as a private issue, with your text and the screenshots you add. Diagnostics are on by default, and you see them before you send. They are the App and command-line versions, your system and its architecture, the versions of Claude Code and Codex, the kind of page you were on, your licence, and how many errors of which kinds happened in the last hour. Never your code, plan or document text, task titles, repository or branch names, or file paths. Screenshots can show code or plans.",
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
    "Is there a limit on tasks or repositories?",
    "No. Each plan is per developer, for as many tasks, repositories and agents as you use.",
  ),
  faq(
    "Which agents does it work with?",
    "Claude Code and Codex, in the terminal, their desktop apps or your IDE; the App sets both up for you. For another coding agent, the App copies a prompt you can hand it. A second opinion from the other coding agent, which runs by itself on risky plans, needs Claude Code and Codex.",
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
    "Enterprise is built with you when your company asks for it: hosting in your own cloud or on-premise, volume pricing, single sign-on, advanced metrics and custom terms. Write to us and we will scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "The App replaces Pilot Shell on first start, and Pilot Shell’s own updater moves you over too. It asks nothing: the tools Pilot Shell installed and its memories stay, and your agent can remove what you no longer need. Your plans carry over and a paid licence keeps working; without one, your 7-day trial starts.",
  ),
];
