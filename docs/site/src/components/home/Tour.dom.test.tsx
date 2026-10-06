// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { useState } from "react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Window } from "happy-dom";
import { afterEach, expect, it } from "vitest";
import { CHAPTERS } from "@/lib/tour";
import TourScenes from "./TourScenes";

afterEach(cleanup);

it("keeps hidden tour overlays from blocking the design's Retry button", async () => {
  const css = readFileSync(join(dirname(fileURLToPath(import.meta.url)), "../../styles/tour.css"), "utf8");
  const window = new Window();
  const style = window.document.createElement("style");
  style.textContent = css;
  window.document.head.append(style);
  window.document.body.innerHTML = '<div class="sx-composer sx-in">Hidden composer</div>';
  const composer = window.document.querySelector(".sx-composer")!;
  expect(window.getComputedStyle(composer).pointerEvents).toBe("none");
  composer.classList.add("on");
  expect(window.getComputedStyle(composer).pointerEvents).toBe("auto");
  await window.happyDOM.close();
});

it("keeps proof visible in the narrow tour after compact document rules apply", async () => {
  const css = readFileSync(join(dirname(fileURLToPath(import.meta.url)), "../../styles/tour-app.css"), "utf8");
  for (const chapter of ["verify", "review"]) {
    const window = new Window();
    const style = window.document.createElement("style");
    style.textContent = css;
    window.document.head.append(style);
    const view = render(<div className="sx-nw"><TourScenes ch={CHAPTERS.findIndex((c) => c.id === chapter)} step={5} tries={2} onRetry={() => {}} only /></div>);
    window.document.body.innerHTML = view.container.innerHTML;
    const points = window.document.querySelector(".sx-proof-points")!;
    expect(window.getComputedStyle(points).display, chapter).toBe("grid");
    expect(points.querySelectorAll(".sx-proof-point")).toHaveLength(3);
    for (const point of points.querySelectorAll(".sx-proof-point")) expect(window.getComputedStyle(point).display).toBe("flex");
    view.unmount();
    await window.happyDOM.close();
  }
});

it("keeps the full-size design's retry working after the agent replies to its comment", () => {
  function Preview() {
    const [tries, setTries] = useState(2);
    return <TourScenes ch={CHAPTERS.findIndex((c) => c.id === "comment")} step={6} tries={tries} onRetry={() => setTries((n) => Math.min(3, n + 1))} only />;
  }
  render(<Preview />);
  expect(screen.getByText(/Each failed row now says when it tries next/)).toBeTruthy();
  const retry = screen.getByRole("button", { name: "Retry" });
  const delivery = retry.closest(".sx-dpr")! as HTMLElement;
  expect(within(delivery).getByText("Try 2 of 3")).toBeTruthy();
  expect((retry as HTMLButtonElement).disabled).toBe(false);
  fireEvent.click(retry);
  expect(within(delivery).getByText("Stopped, mailed")).toBeTruthy();
  expect((retry as HTMLButtonElement).disabled).toBe(true);
});
