import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const schemas = Array.from(
  html.matchAll(
    /<script type="application\/ld\+json">\s*([\s\S]*?)<\/script>/g,
  ),
  (match) => JSON.parse(match[1]) as Record<string, unknown>,
);

const schema = (type: string) => {
  const value = schemas.find((item) => item["@type"] === type);
  expect(value, `missing ${type} JSON-LD`).toBeDefined();
  return value!;
};

const staticNoscript = Array.from(
  html.matchAll(/<noscript>([\s\S]*?)<\/noscript>/g),
  (match) => match[1],
).find((content) => content.includes("What Pilot Shell adds"));

const staticText = staticNoscript
  ?.replace(/<[^>]+>/g, " ")
  .replaceAll("&amp;", "&")
  .replace(/\s+/g, " ")
  .trim();

describe("static marketing shell", () => {
  it("keeps workflows prominent without publishing a Codex operating model", () => {
    const software = schema("SoftwareApplication");
    const features = (software.featureList as string[]).join("\n");

    expect(features).toContain(
      "Spec-Driven Development: plan, approve, implement, verify",
    );
    expect(features).toContain(
      "Quality Checks: workflow-integrated linting, type checking, TDD, and execution verification",
    );
    expect(features).toContain("LSP Integrations: Claude Code only");
    expect(features).toContain(
      "Conditional UI Design Expertise — path-gated principles, progressively disclosed skills, and on-demand Claude Design access",
    );
    expect(features).not.toContain("$spec");
    expect(features).not.toContain("workflow-time checks in Codex");
  });

  it("describes Codex as a supported agent without private policy details", () => {
    const faq = schema("FAQPage");
    const questions = faq.mainEntity as Array<{
      name: string;
      acceptedAnswer: { text: string };
    }>;
    const answer = questions.find((item) =>
      item.name.includes("other AI coding tools"),
    )?.acceptedAnswer.text;

    expect(answer).toContain("agent-specific integrations");
    expect(answer).toContain("Claude Code and Codex CLI");
    expect(answer).not.toContain("/goal");
    expect(answer).not.toContain("$spec");
    expect(answer).not.toContain("proactive subagents");
    expect(answer).not.toContain("routine hooks stay quiet");
    expect(answer).not.toContain(
      "Every hook, rule, command, and workflow is engineered for both",
    );
  });

  it("keeps Claude workflows prominent and Codex compatibility neutral", () => {
    const howTo = schema("HowTo");
    const steps = (howTo.step as Array<{ text: string }>).map(
      (step) => step.text,
    );

    expect(steps[2]).toContain("Claude Code: run /setup-rules");
    expect(steps[3]).toContain("Claude Code: use /spec");
    expect(steps.join(" ")).not.toContain("$spec");
    expect(steps.join(" ")).not.toContain("/goal");

    expect(staticText).toContain(
      "Quality Checks - Workflow-integrated linting, type checking, TDD, and execution verification.",
    );
    expect(staticText).toContain("LSP Integrations - Claude Code only.");
    expect(staticText).toContain(
      "Conditional UI Design Expertise - Path-gated principles, progressively disclosed skills, and on-demand Claude Design access for current Codex.",
    );
    expect(staticText).toContain(
      "Codex compatibility is included through supported integrations.",
    );
    expect(staticText).not.toContain("$spec");
    expect(staticText).not.toContain("/goal");
    expect(staticText).not.toContain("quiet workflow-time checks");
  });
});
