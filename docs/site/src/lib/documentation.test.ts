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
    const sections = install.split(/^## /m);
    const desktop = sections.find((section) => section.startsWith("On your computer\n"));
    const headless = sections.find((section) => section.split("\n")[0].includes("{#without-a-screen}"));
    expect(desktop).toContain("irm https://qualitylayer.dev/install.ps1 | iex");
    expect(desktop).toContain("This installs the App and the command line");
    expect(headless).toContain("curl -fsSL https://qualitylayer.dev/install.sh | bash");
    expect(headless).toContain("Install QualityLayer where your agent runs");
    expect(headless).toContain("**WSL2**");
    expect(headless).toContain("In your Windows browser");
    expect(headless).not.toContain("install.ps1");
  });

  it("keeps human-only prerequisites unverified for Review while available work continues", () => {
    const implement = doc("steps/implement.md");
    expect(implement).toContain("A login, secret, account or other human-only prerequisite");
    expect(implement).toContain("stays unverified for Review");
    expect(implement).toContain("Available work continues");
    expect(implement).toContain("blocked checks retain their evidence instead of being marked passed");
    expect(implement).toContain("The App never takes the secret");
    expect(implement).toContain("Native permission or sign-in prompts still require their normal response");
    expect(implement).toContain("An explicit stop or pause remains in force");
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
