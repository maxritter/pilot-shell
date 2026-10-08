// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, expect, it } from "vitest";
import CloseUp from "./CloseUps";

afterEach(cleanup);

it("keeps all five named workflow steps together below the compact task header", () => {
  const { container } = render(<CloseUp id="plan" step={0} />);
  const header = container.querySelector(".cu-tb") as HTMLElement;
  const steps = screen.getByRole("list", { name: "Task steps" });
  expect(header.contains(steps)).toBe(false);
  expect(steps.textContent).toBe("DiscussPlanImplementVerifyReview");
  expect(steps.querySelector('[aria-current="step"]')?.textContent).toBe("Plan");
});

it("opens actual agent status from its chip while keeping the build document quiet", () => {
  const { container } = render(<CloseUp id="implement" step={4} />);
  expect(container.querySelector(".cu-stage .cu-at")).toBeNull();
  const summary = container.querySelector('summary[aria-label="Claude Code status"]') as HTMLElement;
  expect(summary).toBeTruthy();
  const panel = summary.closest("details") as HTMLDetailsElement;
  expect(panel.open).toBe(false);
  fireEvent.click(summary);
  expect(panel.open).toBe(true);
  expect(panel.textContent).toContain("Building slice 2 of 3");
  expect(panel.textContent).toContain("3 of 5 tasks committed");
});

it("focuses an unresolved Plan choice, then shows the full document and header approval", () => {
  const view = render(<CloseUp id="plan" step={2} />);
  expect(screen.getByText("When the endpoint recovers, who starts a new attempt?")).toBeTruthy();
  expect(screen.queryByRole("article", { name: "Plan document" })).toBeNull();
  view.rerender(<CloseUp id="plan" step={4} />);
  const document = screen.getByRole("article", { name: "Plan document" });
  expect(document.textContent).toContain("Support can start a new attempt after checking the endpoint");
  expect(document.textContent).toContain("Done means");
  expect(document.textContent).toContain("Slices");
  expect(document.textContent).toContain("Technical findings handled by the planning agent");
  expect(view.container.querySelector(".cu-stage .cu-yt")).toBeNull();
  expect(view.container.querySelector(".cu-workspace-track")?.textContent).toContain("Approve Plan");
  expect(view.container.querySelector(".cu-stage")?.textContent).not.toContain("Approve Plan");
});

it("keeps the full-size design's Retry working after the agent replies to its comment", () => {
  function Preview() {
    const [tries, setTries] = useState(2);
    return <CloseUp id="comment" step={6} tries={tries} onRetry={() => setTries((n) => Math.min(3, n + 1))} />;
  }
  render(<Preview />);
  expect(screen.getByText(/Each failed row now says when it tries next/)).toBeTruthy();
  const retry = screen.getByRole("button", { name: "Retry" }) as HTMLButtonElement;
  const row = retry.closest(".cu-dpr") as HTMLElement;
  expect(row.textContent).toContain("Try 2 of 3");
  expect(retry.disabled).toBe(false);
  fireEvent.click(retry);
  expect(row.textContent).toContain("Stopped, mailed");
  expect(retry.disabled).toBe(true);
});
