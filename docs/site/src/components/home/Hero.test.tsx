// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { SLOGAN } from "@/lib/product";
import Hero from "./Hero";

beforeEach(() => { vi.stubGlobal("fetch", async () => new Response("{}", { status: 503 })); });
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("opens on the slogan the rest of the site and the README use", () => {
  render(<MemoryRouter><Hero /></MemoryRouter>);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe(SLOGAN);
});

it("offers the download and film directly from the hero", () => {
  render(<MemoryRouter><Hero /></MemoryRouter>);
  const download = screen.getAllByRole("link").find(link => link.textContent?.startsWith("Download"));
  expect(download?.getAttribute("href")).toBe("/download");
  expect(screen.getByRole("button", { name: /Watch the film/ })).toBeTruthy();
  expect(screen.queryByText("/ql add usage-based billing")).toBeNull();
  expect(screen.queryByRole("button", { name: /Replay/ })).toBeNull();
});

it("opens the overview film and returns focus when the dialog closes", () => {
  const show = vi.spyOn(HTMLDialogElement.prototype, "showModal").mockImplementation(function () {
    this.open = true;
  });
  try {
    render(<MemoryRouter><Hero /></MemoryRouter>);
    const opener = screen.getByRole("button", { name: /Watch the film/ });
    fireEvent.click(opener);
    const dialog = screen.getByRole("dialog");
    expect(dialog.querySelector("video")?.hasAttribute("controls")).toBe(true);
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "Close" }));
    fireEvent(dialog, new Event("close"));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(opener);
  } finally { show.mockRestore(); }
});
