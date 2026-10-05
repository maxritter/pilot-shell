import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

/**
 * The flow asks its decisions in the agent's terminal; the App beside it shows the detail. The
 * README, the docs and the home page must say that, and none may send the person to the App to
 * approve or ask for changes.
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

const TELLS_THE_APP = [
  /press\s+\**approve/i,
  /click\s+\**approve/i,
  /approve\s+in\s+the\s+app/i,
  /request\s+changes\s+in\s+the\s+app/i,
  /answer[^.\n]{0,60}under\s+\**needs you/i,
];

describe("the chat-first flow in the copy", () => {
  it("never tells the person to approve or request changes in the App", () => {
    const offending = [readme, ...docPages, ...homeCopy, homeIndex].flatMap((path) => {
      const text = read(path);
      return TELLS_THE_APP.filter((pattern) => pattern.test(text)).map((pattern) => `${path.replace(`${repo}/`, "")}: ${pattern}`);
    });
    expect(offending).toEqual([]);
  });

  it("says once, in the README, the first task, the home page and its static copy, that the agent asks in the terminal while the App beside it shows the detail", () => {
    const layout = /asks[^.]*in the terminal[^.]*App beside it shows only what the current question is about/gi;
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
