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

/** Words of the App before questions moved into it and designs replaced the files and the agent's switch. */
const STALE = [/for you\s*\/\s*for the agent|for the agent["”*]*\s+switch|\*\*for the agent\*\*/i, /\bfiles tab\b/i, /\bdefault_mode_request_user_input\b/, /\b(option|question)[ -]picker\b/i, /\bpicker hooks?\b/i, /\bsync(ed|s)? (it )?to claude design\b/i];

describe("the flow in the copy: asked and answered in the App", () => {
  it("never tells the person to answer or approve in the terminal or the chat", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return TELLS_THE_TERMINAL.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("names none of the App's removed parts: the agent's switch, the Files tab, the terminal pickers, Claude Design sync", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return STALE.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("describes no Approve menu in the docs: the approval is asked in the terminal", () => {
    // "the Approve menu with its three ways to ship", "open the pull request from the **Approve** menu".
    // The diagnostics page quotes the page kind "Approve menu open" the report sends; that is not an instruction.
    const menu = [/\bthe\s+\**approve\**\s+menu\b/i, /\bfrom\s+the\s+\**approve\b/i];
    const offending = [readme, ...docPages].flatMap((path) => {
      const text = read(path);
      return menu.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
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
});
