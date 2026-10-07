import { spawnSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { COMPARE } from "./pricing";

const repo = fileURLToPath(new URL("../../../../", import.meta.url));
const diagrams = join(repo, "docs/docusaurus/static/img/diagrams");
const read = (path: string) => readFileSync(join(repo, path), "utf8");
const words = (svg: string) => [...svg.matchAll(/<(?:text|title)\b[^>]*>(.*?)<\/(?:text|title)>/gs)].map((m) => m[1]).join(" ");

describe("current public illustrations and guides", () => {
  it("regenerates every diagram from its source without restoring the old interaction", () => {
    const output = mkdtempSync(join(tmpdir(), "ql-public-diagrams-"));
    try {
      const run = spawnSync("python3", [join(repo, "docs/docusaurus/scripts/diagrams.py"), output], { encoding: "utf8" });
      expect(run.status, run.stderr).toBe(0);
      const images = readdirSync(output).filter((name) => name.endsWith(".svg"));
      expect(images.length).toBeGreaterThan(70);
      for (const name of images) {
        const svg = readFileSync(join(output, name), "utf8");
        expect(svg, `${name} is stale; regenerate diagrams.py`).toBe(readFileSync(join(diagrams, name), "utf8"));
        expect(words(svg), name).not.toMatch(/\bNeeds you\b|one question at a time|question (?:N|\d+)\b|Approving takes the open ones|nothing to type here/i);
      }
    } finally {
      rmSync(output, { recursive: true, force: true });
    }
  });

  it("shows full-width numbered focus choices, changed agreements and evidence by point", () => {
    for (const theme of ["light", "dark"]) {
      const drawing = (name: string) => words(read(`docs/docusaurus/static/img/diagrams/${name}-${theme}.svg`));
      expect(drawing("discuss")).toContain("Waits for you");
      expect(drawing("discuss")).toContain("Each answer reaches the agent immediately.");
      for (const step of ["discuss", "plan", "app", "review"]) {
        const svg = read(`docs/docusaurus/static/img/diagrams/${step}-${theme}.svg`);
        const choices = [...svg.matchAll(/<rect data-choice="(\d+)" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"/g)].map((m) => m.slice(1).map(Number));
        expect(choices.map(([n]) => n)).toEqual([1, 2]);
        expect(choices.every(([, x, , width]) => x === 278 && width === 810)).toBe(true);
        expect(choices[1]![2]).toBeGreaterThan(choices[0]![2]!);
        expect(svg).toContain('data-own-words="true"');
        expect(drawing(step)).toContain("Your own answer");
        expect(drawing(step)).toContain("Send");
      }
      expect(drawing("plan")).toMatch(/Was:.*Now:/);
      expect(drawing("plan")).toContain("Answers do not approve the Plan");
      for (const step of ["verify", "review"]) {
        expect(drawing(step)).toMatch(/Done means · 1.*scenario 1.*Done means · 2.*scenario 2/);
      }
      expect(drawing("verify")).toContain("Agent’s turn");
      for (const step of ["app", "discuss", "plan", "implement", "verify", "review"]) {
        const svg = read(`docs/docusaurus/static/img/diagrams/${step}-${theme}.svg`);
        const sidebar = [...svg.matchAll(/<text\b[^>]*>(Files|Comments)<\/text>/g)].map((m) => m[1]);
        expect(sidebar).toEqual(["Files", "Comments"]);
        expect(drawing(step)).toMatch(/Files.*Comments.*Designs/);
      }
      expect(drawing("items")).toContain("In Your turn");
      expect(drawing("items")).not.toContain("In your agent");
      expect(drawing("designs")).toContain("A share link can show a still picture");
    }
  });

  it("keeps independent batch behavior and truthful review provenance in the guides and tour", () => {
    const discuss = read("docs/docusaurus/docs/steps/discuss.md");
    expect(discuss).toMatch(/groups the questions.*batch/);
    expect(discuss).toContain("Answer in any order");
    expect(discuss).toMatch(/immediately|at once/);
    expect(read("docs/site/src/lib/tour.ts")).toContain("a local fallback is a self-review");
    expect(read("docs/site/src/lib/tour.ts")).not.toContain("A second agent reads the Plan before it reaches you");
  });

  it("does not promise that a build can never need its owner", () => {
    const readme = read("README.md");
    expect(readme).not.toMatch(/No waiting while it builds|Nothing waits for you/);
    expect(readme).toContain("other slices keep building");
    expect(read("docs/docusaurus/docs/steps/implement.md")).toContain("**Your turn** names the slice");
  });

  it("includes immediate batches and changed points in the pricing comparison", () => {
    const rows = COMPARE.flatMap((group) => group.rows);
    const batch = rows.find((row) => /questions in batches/.test(row.feature));
    expect(batch?.note).toMatch(/immediately.*Your turn/);
    expect(batch?.solo).toBe(true);
    expect(batch?.team).toBe(true);
    expect(rows.find((row) => /Done means point separately/.test(row.feature))?.note).toMatch(/old and new words/);
  });
});
