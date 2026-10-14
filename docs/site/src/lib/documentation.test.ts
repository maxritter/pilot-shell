import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const doc = (path: string) => readFileSync(new URL(`../../../docusaurus/docs/${path}`, import.meta.url), "utf8");

describe("installation and build instructions", () => {
  // The README stays short (Max, 2026-10-14): it names the opt-in; the build command lives in the docs.
  it("uses direct Claude workflow opt-in in the README", () => {
    const readme = readFileSync(new URL("../../../../README.md", import.meta.url), "utf8");
    expect(readme).not.toContain("/goal /ql implement");
    expect(readme).toContain("QualityLayer runs only when you ask for it");
  });
  it("puts native Windows PowerShell installation with the App and WSL with Linux", () => {
    const install = doc("install.md");
    const [desktop, rest] = install.split("## Without a screen");
    const headless = rest.split("\n## ")[0];
    expect(desktop).toContain("irm https://qualitylayer.dev/install.ps1 | iex");
    expect(desktop).toContain("This installs the App and the command line");
    expect(headless).toContain("curl -fsSL https://qualitylayer.dev/install.sh | bash");
    expect(headless).toContain("inside your Linux distribution");
    expect(headless).not.toContain("install.ps1");
  });

  it("explains what to do when only the person can unblock a build", () => {
    const implement = doc("steps/implement.md");
    expect(implement).toMatch(/login, a secret/);
    expect(implement).toContain("Set it in your own environment");
    expect(implement).toContain("It's set");
    expect(implement).toContain("Other slices keep building");
    expect(implement).toContain("the agent waits for that need to be resolved");
    expect(implement).not.toMatch(/never stops to wait|Nothing waits for you/);
  });

  it("includes the document argument required to open an approval", () => {
    expect(doc("reference/commands.md")).toContain("qualitylayer gate open 03-plan.md");
    expect(doc("reference/commands.md")).toContain("gate open final");
  });

  it("explains live shared updates and preserved drafts without asking guests to reload", () => {
    const sharing = doc("team/plans.md");
    expect(sharing).toContain("The open page updates as the task changes");
    expect(sharing).toContain("keeps your unsent answers and comments");
    expect(sharing).not.toContain("Reload the page");
    expect(sharing).not.toContain("with the time it was last updated");
  });
});
