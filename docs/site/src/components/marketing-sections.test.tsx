import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import ConsoleSection from "./ConsoleSection";
import DeepDiveSection from "./DeepDiveSection";
import HeroSection from "./HeroSection";
import InstallSection from "./InstallSection";
import WhatsInside from "./WhatsInside";
import WorkflowSteps from "./WorkflowSteps";

vi.mock("./Logo", () => ({
  default: () => <span aria-hidden="true">Pilot Shell</span>,
}));
vi.mock("@/components/ImageModal", () => ({
  default: ({ alt }: { alt: string }) => <span>{alt}</span>,
}));

describe("agent-aware marketing sections", () => {
  it("leads with Pilot workflows and keeps agent support neutral", () => {
    const hero = renderToStaticMarkup(<HeroSection />);
    const workflow = renderToStaticMarkup(<WorkflowSteps />);

    expect(hero).toContain("From requirement to production-grade code");
    expect(hero).toContain("Spec-driven plans");
    expect(workflow).toContain("Pilot workflows for every stage");
    expect(workflow).toContain("Supported agents");
    expect(workflow).toContain("Claude Code and Codex");
    expect(workflow).toContain("/spec");
    expect(workflow).toContain("/build");
    expect(workflow).toContain("/fix");
    expect(workflow).toContain("Four core workflows");
    expect(workflow).toContain("Additional workflows and skills");

    const primarySuite = workflow.slice(
      workflow.indexOf("Cross-agent workflow suite"),
      workflow.indexOf("Four core workflows"),
    );
    expect(primarySuite).toContain("/prd");
    expect(primarySuite).toContain("/spec");
    expect(primarySuite).toContain("/build");
    expect(primarySuite).toContain("/fix");
    expect(primarySuite).not.toContain("/investigate");
    expect(primarySuite).not.toContain("/cleanup");

    const additionalSuite = workflow.slice(
      workflow.indexOf("Additional workflows and skills"),
    );
    expect(additionalSuite).toContain('href="/docs/workflows/investigate"');
    expect(additionalSuite).toContain('href="/docs/workflows/cleanup"');
    expect(additionalSuite).toContain("report-only cleanup inventory");
    expect(additionalSuite).toContain("file-and-line evidence");
    expect(additionalSuite).toContain("without changing the project");
    expect(additionalSuite).not.toContain('href="/docs/workflows/prd"');
    expect(additionalSuite).not.toContain('href="/docs/workflows/spec"');
    expect(additionalSuite).not.toContain('href="/docs/workflows/build"');
    expect(additionalSuite).not.toContain('href="/docs/workflows/fix"');
    expect(workflow).not.toContain("Codex defaults");
    expect(workflow).not.toContain("/goal");
    expect(workflow).not.toContain("$spec");
    expect(workflow).not.toContain("bounded independent work");
    expect(workflow).not.toContain("anything multi-file");
  });

  it("leads installation with workflows and names Codex support neutrally", () => {
    const install = renderToStaticMarkup(<InstallSection />);

    expect(install).toContain("Start with");
    expect(install).toContain("/setup-rules");
    expect(install).toContain("/spec");
    expect(install).toContain("/build");
    expect(install).toContain("Pilot Shell also supports");
    expect(install).toContain("Codex CLI");
    expect(install).toContain("ChatGPT app");
    expect(install).not.toContain("$spec");
    expect(install).not.toContain("/goal");
    expect(install).not.toContain("direct requests");
    expect(install).toContain('aria-live="polite"');
    expect(install).toMatch(
      /<code[^>]*overflow-x-auto[^>]*tabindex="0"[^>]*>/,
    );
  });

  it("presents workflow features without a private Codex operating model", () => {
    const features = renderToStaticMarkup(<WhatsInside />);

    expect(features).toContain("Workflow-Driven Development");
    expect(features).toContain("/spec");
    expect(features).toContain("/build");
    expect(features).toContain("/fix");
    expect(features).toContain("Claude Code and Codex");
    expect(features).not.toContain("Codex profile:");
    expect(features).not.toContain("bounded independent work");
    expect(features).not.toContain("routine lifecycle hooks stay quiet");
    expect(features).not.toContain("native safety");
    expect(features).toContain("Claude Code can switch models");
  });

  it("describes the public Claude Code hook pipeline without Codex internals", () => {
    const deepDive = renderToStaticMarkup(<DeepDiveSection />);

    expect(deepDive).toContain("Claude Code hook pipeline");
    expect(deepDive).toContain("file_checker.py");
    expect(deepDive).not.toContain("Codex lifecycle");
    expect(deepDive).not.toContain("Routine Codex hooks stay quiet");
    expect(deepDive).not.toContain("proactive subagents");
    expect(deepDive).not.toContain("explicit $ skills");
    expect(deepDive).not.toContain(
      "fires automatically on both Claude Code and Codex",
    );
  });

  it("renders the screenshot selector as an accessible, responsive tab interface", () => {
    const consoleSection = renderToStaticMarkup(<ConsoleSection />);

    expect(consoleSection).toContain("Track Pilot workflows");
    expect(consoleSection).toContain('role="tablist"');
    expect(consoleSection).toContain('role="tab"');
    expect(consoleSection).toContain('aria-selected="true"');
    expect(consoleSection).toContain('role="tabpanel"');
    expect(consoleSection).toContain("overflow-x-auto");
  });
});
