import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

/**
 * The flow asks every question in the App, the approvals included, and the agent's terminal shows
 * a single line while it waits. The README, the docs and the home page must say that, and none may
 * send the person to the terminal or the chat to answer.
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

const TELLS_THE_TERMINAL = [
  // "asks each decision in the terminal", "you answer in the terminal", "approve in the terminal"
  /\b(asks?|answer(s|ed)?|approve)\b[^.\n]{0,60}\bin\s+the\s+(terminal|chat)\b/i,
  /\bin\s+(its|their|your agent['\u2019]s)\s+own\s+window\b/i,
  /answered in the chat/i,
];

/** Removed controls and serialized delivery. A batch still displays one focused question. */
const STALE = [/for you\s*\/\s*for the agent|for the agent["”*]*\s+switch|\*\*for the agent\*\*/i, /\b(?:agent|QualityLayer|it) asks? one question at a time\b/i, /\basks them one by one\b/i, /\bdefault_mode_request_user_input\b/, /\b(option|question)[ -]picker\b/i, /\bpicker hooks?\b/i, /\bsync(ed|s)? (it )?to claude design\b/i];

describe("the flow in the copy: asked and answered in the App", () => {
  it("never tells the person to answer or approve in the terminal or the chat", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return TELLS_THE_TERMINAL.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("names none of the removed controls or serialized question delivery", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return STALE.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("keeps focused questions inside independent batches with answer order and Skip", () => {
    for (const path of [readme, join(docs, "app.md"), join(docs, "steps/discuss.md")]) {
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
    const pages = [readme, firstTask, join(docs, "steps/discuss.md"), join(docs, "app.md"), join(site, "src/lib/content.ts"), join(site, "src/lib/tour.ts"), homeIndex];
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
    expect(text).toMatch(/one decision at a time/i);
    expect(text).toMatch(/Previous/);
    expect(text).toMatch(/Next/);
    expect(text).toMatch(/diagram or design/i);
    expect(text).toMatch(/own words and \*\*Send\*\* stay visible/i);
    expect(text).toMatch(/each answer reaches your agent immediately/i);
    expect(text).toMatch(/approve/i);
    expect(text).toMatch(/Approving the Plan is a separate action after you settle its decisions/);
    expect(text).toMatch(/Sending answers does not approve it/);
  });

  it("keeps the terminal wait explanation in the guides and shows the batch interaction on the home page", () => {
    const layout = /asks each decision in the App, and its terminal shows a single line while it waits/gi;
    const home = homeCopy.map(read).join("\n");
    for (const [name, text] of Object.entries({ README: read(readme), "first task": read(firstTask), "home page for crawlers": read(homeIndex) })) {
      expect(text.match(layout)?.length, name).toBe(1);
    }
    expect(home).toContain("Questions arrive together in Your turn");
    expect(home).toContain("Answer in any order");
    expect(home).toContain("each answer reaches your agent at once");
  });

  it("names no command that opens the App from Claude Code", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].filter((path) => !path.endsWith("changelog.md") && /\/ql-app\b/.test(read(path)));
    expect(offending).toEqual([]);
  });

  it("documents ql as the only installed command beginning with ql", () => {
    const guarantee = "`/ql` is the only command you need: QualityLayer adds no other command that starts with ql. The `agent-peers` skill works on its own when you ask one agent session to message another.";
    const commands = read(join(docs, "reference/commands.md"));
    expect(read(readme).split("What gets installed")[1]?.split("</details>")[0]).toContain(guarantee);
    expect(commands.split("## In your agent")[1]?.split("## For you")[0]).toContain(guarantee);
    expect(commands).toContain("`/task-pane`");
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].filter((path) => /[/$]ql-[a-z]/i.test(read(path)));
    expect(offending).toEqual([]);
  });
});
