import { VERIFY_CHECKS } from "@/lib/tour";

/**
 * What each chapter's text says, as the words its close-up must show. The close-up opens on a
 * moment that already shows the claim, so a reader who stops on the text sees it at once, and no
 * later moment takes it away.
 * - always: shown at every moment, first to last.
 * - first: shown when the chapter opens.
 * - last: shown once the close-up has finished playing.
 */
export type Claim = { always: (string | RegExp)[]; first?: (string | RegExp)[]; last?: (string | RegExp)[] };

export const CLAIMS: Record<string, Claim> = {
  // "Your agent asks one batch until the goal is clear": the batch's strip, one question in focus, its choices
  discuss: {
    always: [/a batch of 4 from Claude Code/, /Scope and what Done means 1 2 3 4/, /question \d of 4/, "recommended", "Or write your own answer"],
    first: ["question 1 of 4", "Your turn · 4 questions"],
    last: ["Sent to Claude Code", "Your turn · 2 questions"],
  },
  // "Agents read the code before anything is designed", then one more batch when real choices are left
  research: {
    always: ["The questions", "never see your request", "Reading the code, without your request"],
    first: ["3 agents reading the code", "reading the code"],
    last: ["A choice the code leaves open", "From Research"],
  },
  // "You approve one plan before any code": the complete Plan, with its diagram, contracts and outcomes, approved from its header
  plan: {
    always: ["Retry failed webhook deliveries", "Done means", "What happens to a failed delivery", "Contracts", "Reviewed by", "Ready to approve", "Give feedback", "Approve Plan"],
    last: ["1 comment"],
  },
  // "The build is cut into slices while you read the Plan": waves, slices, the scenario for each point, nothing to approve
  outline: {
    always: ["How the build runs", "Wave 2", "Slices 2 and 3, side by side", "How each point is proved", "scenario 3"],
    last: ["Checked by a second reader"],
  },
  // "One command starts the build": the Build defaults in one line and the command
  start: {
    always: ["Plans each slice", "Builds", "Effort", "/ql implement retry-webhooks"],
    first: ["Copy"],
    last: ["Copied"],
  },
  // "It is built in slices, on its own": test first, slices that don't overlap side by side
  implement: {
    always: ["Slices that don’t overlap build side by side", "Every task starts with a failing test", "tasks committed"],
    first: ["building slices 2 and 3 side by side", "2 of 5 tasks committed", "the test fails first"],
    last: ["5 of 5 tasks committed", "built side by side with slice", "Checked by agents", "Ask why"],
  },
  // "Agents that did not write the code check it": six checks in order, each point with its evidence, the chip names what runs
  verify: {
    always: [...VERIFY_CHECKS, "each point against the running program"],
    first: ["running Polish", "delivery.test.ts"],
    last: ["12 of 12 passed", "Your turn · 2 in Review"],
  },
  // "You approve the finished change, with its proof": what only you can confirm, what the agent decided, then Approve
  review: {
    always: [/live call to the partner API/, /retry delay/, "3 of 3 points passed"],
    first: ["Only you can confirm", "I confirm", "Fine", "Ask why", "2 things, then approve"],
    last: ["Approve the change?", "Approve and open a pull request", "with the proof"],
  },
  // "Ask, and your agent draws the page": the request, and the page inside the Plan's question
  draw: {
    always: ["Mock up the failed deliveries page", "the design for this question", "Full size", "Looks right", "Change it"],
  },
  // "Open it full size and point at what to change"
  comment: {
    always: ["failed-deliveries · full size", "Comment", "Retry"],
    first: ["Click a spot on the design"],
    last: ["Each failed row now says when it tries next"],
  },
  // "Ask a teammate about any part of the plan": the passage, who to ask, the Slack message
  ask: {
    always: ["03-plan.md", "one minute apart"],
    first: ["Ask the team about this passage", "Dana", "Ask Dana"],
    last: ["Slack message sent", "via Claude Code"],
  },
  // "Teammates see the questions for them first": the passage in view, a draft that is not sent
  answer: {
    always: ["Question from Max Ritter", "one minute apart", "Looks right", "Suggest a change", "Reply", "Or hand it to someone else"],
    last: ["Draft by your Claude Code · not sent yet"],
  },
  // "See your team's work in one place": remind or hand on
  space: {
    always: ["Your questions to others", "Working now", "Team activity", "Remind", "Hand to…"],
    last: ["reminded just now"],
  },
  // "Review the finished change together": the proof, a teammate's comment, then approval
  together: {
    always: ["Done means 3", "Can support see this without the log?", "screenshot 2"],
    first: ["Comment from Ben"],
    last: ["Ready to approve", "Dana approved"],
  },
  // "Choose the models, and see what each step costs"
  settings: {
    always: ["Planning defaults", "Build defaults", "Starts in", "$20.95", "estimated at list price", "never wrote the code"],
    last: ["GPT-6.1 Sol"],
  },
  // "It works where your agents already work": one command, the systems it runs on
  agents: {
    always: ["New task", "Claude Code", "Codex", "Another agent", "claude --model opus --effort high", "macOS", "Windows", "Linux", "WSL"],
    last: ["Copied", "needs your review"],
  },
};

/** The claims in `wanted` that `text` does not show. */
export const missing = (text: string, wanted: (string | RegExp)[] = []) => wanted.filter((w) => (typeof w === "string" ? !text.includes(w) : !w.test(text)));
