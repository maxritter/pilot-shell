// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { useState } from "react";
import { afterEach, expect, it } from "vitest";
import { CHAPTERS } from "@/lib/tour";
import TourScenes from "./TourScenes";

afterEach(cleanup);

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
