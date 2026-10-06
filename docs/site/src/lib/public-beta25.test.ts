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

describe("beta.25 public illustrations and guides", () => {
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

  it("shows a batch, individual changed agreements and evidence by point", () => {
    for (const theme of ["light", "dark"]) {
      const drawing = (name: string) => words(read(`docs/docusaurus/static/img/diagrams/${name}-${theme}.svg`));
      expect(drawing("discuss")).toContain("Answer in any order");
      expect(drawing("discuss")).toContain("Your answer is needed in the QualityLayer App.");
      expect(drawing("plan")).toMatch(/Was:.*Now:/);
      expect(drawing("plan")).toContain("Answers do not approve the Plan");
      for (const step of ["verify", "review"]) {
        expect(drawing(step)).toMatch(/Done means · 1.*scenario 1.*Done means · 2.*scenario 2/);
      }
      expect(drawing("verify")).toContain("Agent’s turn");
      for (const step of ["app", "discuss", "plan", "implement", "verify", "review"]) {
        expect(drawing(step)).toMatch(/Comments.*Files.*Designs/);
      }
      expect(drawing("items")).toContain("In Your turn");
      expect(drawing("items")).not.toContain("In your agent");
      expect(drawing("designs")).toContain("A share link can show a still picture");
    }
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
