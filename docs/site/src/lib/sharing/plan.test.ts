import { describe, expect, it } from "vitest";
import { contractsOf, mockupHtml, mockupName, planBlocks, slicesOf, withCsp } from "./plan";

/**
 * A shared plan's markdown, cut into what the page draws: text, diagrams and mockups. The page
 * has no DOM in these tests, so text arrives as the escaped fallback; what matters is the order
 * and the kind of each part.
 */

const PLAN = [
  "# Settings cleanup",
  "",
  "First the configuration changes.",
  "",
  "```mermaid",
  "graph LR; A-->B",
  "```",
  "",
  "## Interface",
  "",
  "```artifact artifacts/settings.html",
  "```",
  "",
  "A closing remark.",
].join("\n");

describe("a plan cut into parts", () => {
  it("keeps the order: text, a diagram, text, a mockup, text", () => {
    const blocks = planBlocks(PLAN);
    expect(blocks.map((b) => b.kind)).toEqual(["html", "mermaid", "html", "artifact", "html"]);
    expect(blocks[1]).toMatchObject({ kind: "mermaid", source: "graph LR; A-->B" });
    expect(blocks[3]).toMatchObject({ kind: "artifact", path: "artifacts/settings.html" });
  });

  it("never lets the fence's words stand in for the picture", () => {
    const text = planBlocks(PLAN)
      .flatMap((b) => (b.kind === "html" ? [b.html] : []))
      .join("");
    expect(text).not.toContain("artifacts/settings.html");
    expect(text).not.toContain("graph LR");
    expect(text).toContain("First the configuration changes.");
    expect(text).toContain("A closing remark.");
  });

  it("gives every part its own key", () => {
    const keys = planBlocks(PLAN).map((b) => b.key);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("is empty for an empty document", () => {
    expect(planBlocks("")).toEqual([]);
  });
});

const DETAILS = [
  "# Plan details",
  "",
  "## System design contracts",
  "",
  "### A 429 keeps the API's error shape",
  "",
  "The body stays `{ error, retryAfter }`.",
  "",
  "### The limiter lives in one module",
  "",
  "```mermaid",
  "graph TD; R-->L",
  "```",
  "",
  "## Program design",
  "",
  "### `limit(key)` returns the wait",
  "",
  "Signature and invariants.",
  "",
  "## Slice 1: Fewer settings, in the CLI and the App together",
  "",
  "Two sentences.",
  "",
  "- [ ] T1 Remove the budget flag",
  "  - **Objective:** gone.",
  "- [ ] T2 Remove the switch",
  "",
  "## Slice 2: Select all fills a group",
  "",
  "- [x] T3 One change",
  "",
  "## Scenarios and the oracle",
  "",
  "- [ ] not a task of a slice",
].join("\n");

describe("the build's slices", () => {
  it("lists each slice with its title and its tasks", () => {
    expect(slicesOf(DETAILS)).toEqual([
      { n: 1, title: "Fewer settings, in the CLI and the App together", tasks: 2 },
      { n: 2, title: "Select all fills a group", tasks: 1 },
    ]);
  });

  it("finds none in a document without any", () => {
    expect(slicesOf("# Just a plan\n\nText.")).toEqual([]);
  });
});

describe("the contracts the build must keep", () => {
  it("takes each H3 under the contract sections, with its body", () => {
    const contracts = contractsOf(DETAILS);
    expect(contracts.map((c) => c.title)).toEqual([
      "A 429 keeps the API's error shape",
      "The limiter lives in one module",
      "`limit(key)` returns the wait",
    ]);
    expect(contracts[0]?.body).toContain("retryAfter");
    expect(contracts[1]?.body).toContain("```mermaid");
  });

  it("ignores H3s elsewhere", () => {
    expect(contractsOf("## Risks\n\n### A risk\n\nText.")).toEqual([]);
  });
});

describe("a mockup's page", () => {
  it("gets the policy before any of its own scripts, and never mistakes a <header> for the <head>", () => {
    const withHead = withCsp("<!doctype html><html><head><title>x</title></head><body><script>1</script></body></html>");
    expect(withHead.indexOf("Content-Security-Policy")).toBeLessThan(withHead.indexOf("<title>"));
    const headerOnly = withCsp('<html lang="en"><body><header class="top">Hi</header><script>1</script></body></html>');
    expect(headerOnly).toMatch(/^<html lang="en"><head><meta http-equiv="Content-Security-Policy"/);
    expect(headerOnly.indexOf("Content-Security-Policy")).toBeLessThan(headerOnly.indexOf("<script>"));
    expect(withCsp("<h1>bare</h1>")).toMatch(/^<head><meta .*<h1>bare<\/h1>$/);
  });

  it("is found by the plan's path or by the bare name a question gives", () => {
    const docs = { "artifacts/settings.html": "<p>m</p>" };
    expect(mockupHtml(docs, "artifacts/settings.html")).toBe("<p>m</p>");
    expect(mockupHtml(docs, "settings.html")).toBe("<p>m</p>");
    expect(mockupHtml(docs, "other.html")).toBeUndefined();
    expect(mockupName("artifacts/settings.html")).toBe("settings.html");
  });
});
