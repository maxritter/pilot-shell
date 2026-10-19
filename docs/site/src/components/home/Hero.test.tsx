// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { BRAND_LINE, SLOGAN } from "@/lib/product";
import Hero from "./Hero";

beforeEach(() => { vi.stubGlobal("fetch", async () => new Response("{}", { status: 503 })); });
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("opens on the brand line and the slogan the rest of the site and the README use", () => {
  render(<MemoryRouter><Hero /></MemoryRouter>);
  const h1 = screen.getByRole("heading", { level: 1 });
  expect(h1.textContent).toBe(SLOGAN);
  expect(h1.previousElementSibling?.textContent).toBe(BRAND_LINE);
});

it("lists the seven steps as stations that each open their step in the tour", () => {
  render(<MemoryRouter><Hero /></MemoryRouter>);
  const stations = within(screen.getByRole("navigation", { name: "The seven steps" })).getAllByRole("listitem");
  expect(stations.map((s) => s.querySelector(".mx-station-name")?.lastChild?.textContent)).toEqual(["Discuss", "Research", "Plan", "Outline", "Implement", "Verify", "Review"]);
  expect(stations.map((s) => within(s).getByRole("link").getAttribute("href"))).toEqual(["/#discuss", "/#research", "/#plan", "/#outline", "/#implement", "/#verify", "/#review"]);
  expect(screen.getByRole("link", { name: "See each step in the App" }).getAttribute("href")).toBe("/#plan");
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
