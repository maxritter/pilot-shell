// @vitest-environment happy-dom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import Hero from "./Hero";

beforeEach(() => { vi.stubGlobal("fetch", async () => new Response("{}", { status: 503 })); });
afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals(); });

it("plays the illustrative prompt once, replays manually and cancels work on unmount", async () => {
  vi.useFakeTimers();
  const view = render(<MemoryRouter><Hero /></MemoryRouter>);
  expect(screen.getByText("Illustrative prompt; no task is submitted.")).toBeTruthy();
  await act(() => vi.advanceTimersByTime(2500));
  expect(document.querySelector(".sx-prompt-typed")?.textContent).toBe("/ql add usage-based billing");
  fireEvent.click(screen.getByRole("button", { name: "Replay prompt" }));
  expect(document.querySelector(".sx-prompt-typed")?.textContent).toBe("");
  view.unmount();
  expect(vi.getTimerCount()).toBe(0);
});

it("keeps the full prompt readable in reduced motion", () => {
  const media = window.matchMedia("(prefers-reduced-motion: reduce)");
  Object.defineProperty(media, "matches", { value: true });
  const original = window.matchMedia;
  window.matchMedia = () => media;
  try {
    render(<MemoryRouter><Hero /></MemoryRouter>);
    expect(document.querySelector(".sx-prompt-typed")?.textContent).toBe("/ql add usage-based billing");
    expect(screen.queryByRole("button", { name: "Replay prompt" })).toBeNull();
  } finally { window.matchMedia = original; }
});

it("cancels typing while the document is hidden and resumes at the same position", async () => {
  vi.useFakeTimers();
  render(<MemoryRouter><Hero /></MemoryRouter>);
  await act(() => vi.advanceTimersByTime(90));
  const text = document.querySelector(".sx-prompt-typed")!;
  expect(text.textContent).toBe("/q");
  Object.defineProperty(document, "hidden", { configurable: true, value: true });
  fireEvent(document, new Event("visibilitychange"));
  expect(vi.getTimerCount()).toBe(0);
  await act(() => vi.advanceTimersByTime(1000));
  expect(text.textContent).toBe("/q");
  Object.defineProperty(document, "hidden", { configurable: true, value: false });
  fireEvent(document, new Event("visibilitychange"));
  await act(() => vi.advanceTimersByTime(45));
  expect(text.textContent).toBe("/ql");
  delete (document as unknown as { hidden?: boolean }).hidden;
});
