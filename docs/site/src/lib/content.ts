/**
 * The website's questions and answers. Each answer must hold for the product as it
 * ships; when the product changes, change it here. Plain text only: the home page's
 * structured data reuses these answers.
 */

export type Faq = { question: string; answer: string };

const faq = (question: string, answer: string): Faq => ({ question, answer });

export const FAQS: Faq[] = [
  faq(
    "How is this different from plan mode in my agent?",
    "Plan mode gives you a plan in the chat. QualityLayer turns it into short documents you approve one by one, with diagrams and clickable mockups. It then builds from them in tested slices, and an AI that did not write the code checks the result, with evidence.",
  ),
  faq(
    "Does it replace my coding agent?",
    "No. Your agent still writes the code, with the model and provider you already pay for. QualityLayer adds the plan you approve, the tests, the checks and the App around it.",
  ),
  faq(
    "What do I actually review?",
    "Short documents written for you: the goal, how the code works today, the design with diagrams and mockups (a PRD and a TDD if you work as a product manager), and the slices. At the end: what was checked, the evidence, steps to try it, and the diff.",
  ),
  faq(
    "How do I know the change really works?",
    "Every slice starts with a failing test and runs end to end before the next one, and the test output, logs and screenshots are kept. At the end, an AI that did not write the code checks every point of what you asked for.",
  ),
  faq(
    "What about small fixes?",
    "They take the quick route: a failing test, the change, a check, your approval. No planning documents. If the fix turns out bigger, the agent moves it to the full plan.",
  ),
  faq(
    "Does it use more tokens?",
    "Planning and checking add some work. The building is done by smaller, cheaper models, each starting from the short plan instead of your whole chat. In Settings you choose one model for the helpers per agent, or have your agent do every step itself, and each optional step has its own switch.",
  ),
  faq(
    "Can I leave while it builds?",
    "Yes. After the handoff it builds and tests each slice on its own. It stops only when a check keeps failing or a decision is yours, and your browser tells you.",
  ),
  faq(
    "Does my code leave my computer?",
    "Plans are Markdown files in your repository, and the QualityLayer App runs on your computer. Your agent keeps its own provider settings. Sharing with your team sends the plan and its progress, encrypted on your machine so we can’t read it, and never your code.",
  ),
  faq(
    "Which agents work with it?",
    "Any coding agent that supports skills and can run shell commands, in the terminal, its desktop app or its IDE extension. The installer sets up Claude Code and Codex. With both installed, an AI from the other vendor also gives a second opinion on the design and the finished change.",
  ),
  faq(
    "Can my team review plans too?",
    "Yes, with a Team plan. Teammates comment and approve in their own App, and people outside the team comment through a link. Their feedback goes to your agent; you decide.",
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
    "Any AI coding agent that supports skills and can run shell commands, in the terminal, its desktop app or its IDE extension. Claude Code and Codex are set up for you. The second opinion from another vendor’s AI needs both of them.",
  ),
  faq(
    "Who needs a seat?",
    "Each person on your team who uses QualityLayer. People outside your team whom you invite to comment through a link do not need one.",
  ),
  faq(
    "Does my code leave my computer?",
    "Plans are Markdown files in your repository, and the QualityLayer App runs on your computer. Your AI agent keeps its own provider and data settings. When you share a task, its plan is encrypted on your machine first, so we store it but can’t read it. We see who shared it, which task, when and its stage.",
  ),
  faq(
    "What does Enterprise include?",
    "Enterprise is built with you when your company asks for it: hosting in your own cloud or on-premise, volume pricing, single sign-on, advanced metrics and custom terms. Write to us and we will scope it together.",
  ),
  faq(
    "I use Pilot Shell 11. What happens?",
    "Run the installer. It explains the change on one screen, once. In a terminal it lists what goes, lets you pick which of the tools Pilot Shell installed to remove, and asks about its memories, then installs QualityLayer. Your plans carry over and a paid licence keeps working (without one, your 7-day trial starts), and your own agent settings keep working.",
  ),
];
