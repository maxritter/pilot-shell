import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { FAQS } from "./content";
import { CHAPTERS } from "./tour";

/**
 * App is the default answer location. Only the explicit Terminal mode reference may describe
 * answering in chat and native pickers; removed controls stay forbidden in both modes.
 */

const site = fileURLToPath(new URL("../../", import.meta.url));
const repo = join(site, "../..");
const docs = join(repo, "docs/docusaurus/docs");

const read = (path: string) => readFileSync(path, "utf8");

/** Every file under `dir` with one of the extensions, skipping tests. */
function filesUnder(dir: string, extensions: string[]): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return entry.name === "node_modules" ? [] : filesUnder(path, extensions);
    return extensions.some((ext) => entry.name.endsWith(ext)) && !/\.test\./.test(entry.name) ? [path] : [];
  });
}

const readme = join(repo, "README.md");
const firstTask = join(docs, "first-task.md");
const docPages = filesUnder(docs, [".md"]).filter((path) => !path.endsWith("changelog.md"));
const homeCopy = [...filesUnder(join(site, "src/lib"), [".ts"]), ...filesUnder(join(site, "src/components"), [".tsx"]), join(site, "src/pages/Index.tsx")].filter(existsSync);
const homeIndex = join(site, "index.html");
const commandsPage = join(docs, "reference/commands.md");

function modeCopy(path: string, text: string): { app: string; terminal: string } {
  const start = path === commandsPage ? text.indexOf("\n## Terminal mode\n") : -1;
  if (start < 0) return { app: text, terminal: "" };
  const next = text.indexOf("\n## ", start + 1);
  const end = next < 0 ? text.length : next;
  return { app: text.slice(0, start) + text.slice(end), terminal: text.slice(start, end) };
}

const TELLS_THE_TERMINAL = [
  // "asks each decision in the terminal", "you answer in the terminal", "approve in the terminal"
  /\b(asks?|answer(s|ed)?|approve)\b[^.\n]{0,60}\bin\s+the\s+(terminal|chat)\b/i,
  /\bin\s+(its|their|your agent['\u2019]s)\s+own\s+window\b/i,
  /answered in the chat/i,
];

/** Removed controls and serialized delivery. A batch still displays one focused question. */
const STALE = [/for you\s*\/\s*for the agent|for the agent["”*]*\s+switch|\*\*for the agent\*\*/i, /\b(?:agent|QualityLayer|it) asks? one question at a time\b/i, /\basks them one by one\b/i, /\bdefault_mode_request_user_input\b/, /\bsync(ed|s)? (it )?to claude design\b/i];
const NATIVE_PICKERS = [/\b(option|question)[ -]picker\b/i, /\bpicker hooks?\b/i];

describe("the flow in the copy: asked and answered in the App", () => {
  it("keeps default instructions in the App outside the explicit Terminal mode reference", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = modeCopy(path, read(path)).app;
      return TELLS_THE_TERMINAL.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("names none of the removed controls or serialized question delivery", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      const app = modeCopy(path, text).app;
      return [...STALE.filter((pattern) => pattern.test(text)), ...NATIVE_PICKERS.filter((pattern) => pattern.test(app))].map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("allows native answers only in the named opt-in section and retains human approval", () => {
    const { app, terminal } = modeCopy(commandsPage, read(commandsPage));
    expect(app).toContain("Ask you a question in the App and wait for your answer");
    expect(terminal).toContain("Using QualityLayer in the terminal");
    expect(terminal).toContain("Only your own picks or words count as answers and approvals");
    expect(terminal).toMatch(/question picker/);
    const sample = "\n## Terminal mode\nYou answer in the terminal using a question picker.\n## For you\nYou answer in the terminal using a question picker.";
    for (const path of [commandsPage, readme]) {
      const scoped = modeCopy(path, sample);
      expect(TELLS_THE_TERMINAL.some((pattern) => pattern.test(scoped.app))).toBe(true);
      expect(NATIVE_PICKERS.some((pattern) => pattern.test(scoped.app))).toBe(true);
    }
    const removed = "\n## Terminal mode\nQualityLayer asks one question at a time. For you / For the agent.";
    expect(STALE.filter((pattern) => pattern.test(modeCopy(commandsPage, removed).terminal))).toHaveLength(2);
  });

  // The README stays short (Max, 2026-10-14) and links to these guides; they carry the details.
  it("keeps focused questions inside independent batches with answer order and Skip", () => {
    for (const path of [join(docs, "app.md"), join(docs, "steps/discuss.md")]) {
      const text = read(path);
      const name = path.replace(`${repo}/`, "");
      expect(text, name).toMatch(/independent questions|questions it can ask together/i);
      expect(text, name).toMatch(/\bbatch(es)?\b/i);
      expect(text, name).toMatch(/one (focused )?question|shows one with its context/i);
      expect(text, name).toMatch(/answer in any order|answer another first|answer another question first/i);
      expect(text, name).toMatch(/Skip for now/i);
      expect(text, name).toMatch(/immediately|at once/i);
    }
  });

  it("explains batches, Your turn and immediate answers wherever a first-time reader learns the flow", () => {
    const pages = [firstTask, join(docs, "steps/discuss.md"), join(docs, "app.md"), join(site, "src/lib/content.ts"), join(site, "src/lib/tour.ts"), homeIndex];
    for (const path of pages) {
      const text = read(path);
      const name = path.replace(`${repo}/`, "");
      expect(text, name).toMatch(/\bbatch(es)?\b/i);
      expect(text, name).toMatch(/Your turn/i);
      expect(text, name).toMatch(/immediately|at once/i);
    }
  });

  it("explains the Plan's focused decisions, navigation and immediate answers before approval", () => {
    const text = read(join(docs, "steps/plan.md"));
    expect(text).toMatch(/Your turn/i);
    expect(text).toMatch(/shows them one at a time/i);
    expect(text).toMatch(/the part of the Plan each concerns/i);
    expect(text).toMatch(/Findings from the technical review return to the planning agent/i);
    expect(text).toMatch(/Read the complete Plan/i);
    expect(text).toMatch(/each answer reaches your agent immediately/i);
    expect(text).toMatch(/approve/i);
    expect(text).toMatch(/Approve Plan\*\* at the top right/);
    expect(text).toMatch(/Give feedback/);
    expect(text).toMatch(/answering a question does not approve the Plan/);
  });

  it("keeps where each mode asks in the guides and shows the batch interaction on the home page", () => {
    const layout = /asks each decision in the App, and its terminal shows a single line while it waits/gi;
    const home = homeCopy.map(read).join("\n");
    expect(read(homeIndex).match(layout)?.length, "home page for crawlers").toBe(1);
    // An agent outside the App asks in its own chat; the guide never says it asks in the App.
    const guide = read(firstTask);
    expect(guide).toMatch(/When the agent runs in your terminal, app or IDE, it asks each decision in its own chat/);
    expect(guide).not.toMatch(layout);
    expect(home).toContain("Questions arrive together in Your turn");
    expect(home).toContain("Answer in any order");
    expect(home).toContain("each answer reaches your agent at once");
  });

  it("names no command that opens the App from Claude Code", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].filter((path) => !path.endsWith("changelog.md") && /\/ql-app\b/.test(read(path)));
    expect(offending).toEqual([]);
  });

  it("names the two levels in the tour and the FAQ, with where each is picked and switched", () => {
    const discuss = CHAPTERS.find((chapter) => chapter.id === "discuss");
    const tour = [discuss?.title, discuss?.text, ...(discuss?.bullets ?? [])].join(" ");
    const faq = FAQS.map((entry) => `${entry.question} ${entry.answer}`).join(" ");
    for (const [name, text] of Object.entries({ "tour's Discuss chapter": tour, FAQ: faq })) {
      expect(text, name).toMatch(/\bProduct\b/);
      expect(text, name).toMatch(/\bEngineering\b/);
      expect(text, name).toMatch(/\bSetup\b/);
      expect(text, name).toMatch(/Settings › Workflow/);
    }
    expect(faq).toMatch(/task header/i);
  });

  it("gives the README and the docs' intro a part on the two levels that says where to pick and switch", () => {
    for (const path of [readme, join(docs, "intro.md")]) {
      const text = read(path);
      const name = path.replace(`${repo}/`, "");
      const part = (text.split(/^#{2,3} Two levels\s*$/m)[1] ?? "").split(/^#{1,3} /m)[0] ?? "";
      expect(part, name).toMatch(/\bProduct\b/);
      expect(part, name).toMatch(/\bEngineering\b/);
      expect(part, name).toMatch(/\bSetup\b/);
      expect(part, name).toMatch(/Settings › Workflow/);
      expect(part, name).toMatch(/task header/i);
    }
  });

  it("uses natural requests and names capability skills without requiring manual invocations", () => {
    const commands = read(join(docs, "reference/commands.md"));
    const agentCommands = commands.split("## In your agent")[1]?.split("## For you")[0];
    expect(agentCommands).toContain("natural language");
    expect(agentCommands).toContain("QualityLayer");
    expect(agentCommands).toContain("QL");
    for (const name of ["ql-workflow", "ql-artifact", "ql-peer", "ql-manage"]) expect(agentCommands).toContain(name);
    expect(agentCommands).not.toMatch(/[/$]ql(?:\s|`)/);
    expect(commands).toContain("`/task-pane`");
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].filter((path) => /[/$]ql-[a-z]/i.test(read(path)));
    expect(offending).toEqual([]);
  });
});
