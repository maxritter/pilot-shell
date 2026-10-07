// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, expect, it } from "vitest";
import CloseUp from "./CloseUps";

afterEach(cleanup);

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
