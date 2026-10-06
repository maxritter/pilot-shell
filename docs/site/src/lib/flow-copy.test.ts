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

/** Removed controls and the old serialized question flow. Files is a current sidebar tab. */
const STALE = [/for you\s*\/\s*for the agent|for the agent["”*]*\s+switch|\*\*for the agent\*\*/i, /\bone question at a time\b/i, /\basks them one by one\b/i, /\bdefault_mode_request_user_input\b/, /\b(option|question)[ -]picker\b/i, /\bpicker hooks?\b/i, /\bsync(ed|s)? (it )?to claude design\b/i];

describe("the flow in the copy: asked and answered in the App", () => {
  it("never tells the person to answer or approve in the terminal or the chat", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return TELLS_THE_TERMINAL.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("names none of the removed controls or the old one-question flow", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return STALE.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("explains batches, Your turn and immediate answers wherever a first-time reader learns the flow", () => {
    const pages = [readme, firstTask, join(docs, "steps/discuss.md"), join(docs, "steps/plan.md"), join(docs, "app.md"), join(site, "src/lib/content.ts"), join(site, "src/lib/tour.ts"), homeIndex];
    for (const path of pages) {
      const text = read(path);
      const name = path.replace(`${repo}/`, "");
      expect(text, name).toMatch(/\bbatch(es)?\b/i);
      expect(text, name).toMatch(/Your turn/i);
      expect(text, name).toMatch(/immediately|at once/i);
    }
  });

  it("says once, in the README, the first task, the home page and its static copy, that the agent asks in the App while its terminal shows one line", () => {
    const layout = /asks each decision in the App, and its terminal shows a single line while it waits/gi;
    const home = homeCopy.map(read).join("\n");
    for (const [name, text] of Object.entries({ README: read(readme), "first task": read(firstTask), "home page": home, "home page for crawlers": read(homeIndex) })) {
      expect(text.match(layout)?.length, name).toBe(1);
    }
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
