import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import AgentsSection from "./AgentsSection";
import AnatomySection from "./AnatomySection";
import ConsoleSection from "./ConsoleSection";
import HeroSection from "./HeroSection";
import InstallSection from "./InstallSection";
import TeamSection from "./TeamSection";
import WorkflowSteps from "./WorkflowSteps";

vi.mock("@/components/ImageModal", () => ({
  default: ({ alt }: { alt: string }) => <span>{alt}</span>,
}));

describe("agent-aware marketing sections", () => {
  it("leads the hero with the design's harness claim and the install command", () => {
    const hero = renderToStaticMarkup(<HeroSection />);

    expect(hero).toContain("How real engineers run Claude Code and Codex");
    expect(hero).toContain("From requirement to production-grade code");
    expect(hero).toContain("planned, tested, verified.");
    expect(hero).toContain("context and harness engineering");
    expect(hero).toContain("install.sh | bash");
    expect(hero).toContain("macOS · Linux · Windows (WSL2)");
    expect(hero).not.toContain("$spec");
    expect(hero).not.toContain("/goal");
  });

  it("presents the four core workflows and the on-demand commands with doc links", () => {
    const workflow = renderToStaticMarkup(<WorkflowSteps />);

    expect(workflow).toContain("Workflows put the harness around the work.");
    expect(workflow).toContain(
      "Direct requests, native Plan/Goal tools, and Pilot workflows are peers.",
    );
    for (const slug of ["prd", "spec", "build", "fix"]) {
      expect(workflow).toContain(`href="/docs/workflows/${slug}"`);
    }
    expect(workflow).toContain("/prd — brainstorm what to build");
    expect(workflow).toContain("/spec — plan, build, and verify");
    expect(workflow).toContain("/build — name a goal, walk away");
    expect(workflow).toContain("/fix — investigate, test, fix, audit");
    expect(workflow).toContain("Rules, skills, and memory");
    for (const slug of [
      "setup-rules",
      "create-skill",
      "benchmark",
      "investigate",
      "cleanup",
    ]) {
      expect(workflow).toContain(`href="/docs/workflows/${slug}"`);
    }
    expect(workflow).toContain("report-only cleanup inventory");
    expect(workflow).toContain("file-and-line evidence");
    expect(workflow).toContain("without changing the project");
    expect(workflow).not.toContain("Codex defaults");
    expect(workflow).not.toContain("/goal");
    expect(workflow).not.toContain("$spec");
    expect(workflow).not.toContain("bounded independent work");
  });

  it("renders the six harness layers as an accessible tab interface", () => {
    const anatomy = renderToStaticMarkup(<AnatomySection />);

    expect(anatomy).toContain("Six layers of quality. Pick one apart.");
    for (const layer of [
      "Context Engineering",
      "Spec-Driven Delivery",
      "Enforced Quality Gates",
      "Independent Verification",
      "Stateful Delivery &amp; Memory",
      "Human Control Plane",
    ]) {
      expect(anatomy).toContain(layer);
    }
    expect(anatomy).toContain('role="tablist"');
    expect(anatomy).toContain('role="tab"');
    expect(anatomy).toContain('aria-selected="true"');
    expect(anatomy).toContain('role="tabpanel"');
    expect(anatomy).toContain("What it refuses");
    expect(anatomy).toContain("What you get");
    expect(anatomy).toContain(
      "One system for Claude Code and Codex — platform adapters preserve",
    );
  });

  it("leads installation with workflows and names Codex support neutrally", () => {
    const install = renderToStaticMarkup(<InstallSection />);

    expect(install).toContain("Getting Started");
    expect(install).toContain("Start with");
    expect(install).toContain("/setup-rules");
    expect(install).toContain("/spec");
    expect(install).toContain("/build");
    expect(install).toContain("Pilot Shell also supports");
    expect(install).toContain("Codex CLI");
    expect(install).toContain("ChatGPT app");
    expect(install).not.toContain("$spec");
    expect(install).not.toContain("/goal");
    expect(install).toContain('aria-live="polite"');
    expect(install).toMatch(/<code[^>]*overflow-x-auto[^>]*tabindex="0"[^>]*>/);
  });

  it("frames team sharing through the repo, not a cloud", () => {
    const team = renderToStaticMarkup(<TeamSection />);

    expect(team).toContain("Share the why, not just the code.");
    expect(team).toContain("Team memories");
    expect(team).toContain("Extension sharing");
    expect(team).toContain("One standard for everyone");
    expect(team).toContain("no cloud, no clock, you review the diff and commit");
  });

  it("describes both agents with their real coverage and subscriptions", () => {
    const agents = renderToStaticMarkup(<AgentsSection />);

    expect(agents).toContain("Claude Code");
    expect(agents).toContain("Primary — full feature coverage");
    expect(agents).toContain("Codex");
    expect(agents).toContain("All workflows, fewer platform features");
    expect(agents).toContain("$prd");
    expect(agents).toContain("explicit-only");
    expect(agents).toContain("Claude Max, Team Premium, or Enterprise");
    expect(agents).toContain("OpenAI Plus, Pro, Business,");
  });

  it("renders the screenshot selector as an accessible, responsive tab interface", () => {
    const consoleSection = renderToStaticMarkup(<ConsoleSection />);

    expect(consoleSection).toContain("The human control plane");
    expect(consoleSection).toContain("localhost:41777");
    expect(consoleSection).toContain('role="tablist"');
    expect(consoleSection).toContain('role="tab"');
    expect(consoleSection).toContain('aria-selected="true"');
    expect(consoleSection).toContain('role="tabpanel"');
    expect(consoleSection).toContain("overflow-x-auto");
  });
});
