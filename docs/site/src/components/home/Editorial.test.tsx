// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it } from "vitest";
import Editorial from "./Editorial";

afterEach(cleanup);

it("selects any keyboard chapter immediately without depending on a scroll event", () => {
  render(<MemoryRouter><Editorial /></MemoryRouter>);
  const rail = screen.getByRole("list", { name: "The eight steps" });
  const review = within(rail).getByRole("button", { name: "Review" });
  fireEvent.click(review);
  expect(review.getAttribute("aria-current")).toBe("step");
  expect(screen.getByRole("button", { name: "Enlarge Review" })).toBeTruthy();
  const plan = within(rail).getByRole("button", { name: "Plan" });
  fireEvent.click(plan);
  expect(plan.getAttribute("aria-current")).toBe("step");
});

it("keeps an honest caption when an image fails", () => {
  render(<MemoryRouter><Editorial /></MemoryRouter>);
  fireEvent.error(screen.getAllByRole("img")[0]);
  expect(screen.getByText("Discuss image unavailable. Open the preview to retry.")).toBeTruthy();
});

it("marks the image preview as modal and returns focus after Escape", async () => {
  render(<MemoryRouter><Editorial /></MemoryRouter>);
  const open = screen.getByRole("button", { name: "Enlarge Discuss" });
  fireEvent.click(open);
  const preview = await screen.findByRole("dialog", { name: "Discuss" });
  expect(preview.getAttribute("aria-modal")).toBe("true");
  const close = within(preview).getByRole("button", { name: "Close preview" });
  close.focus();
  fireEvent.keyDown(close, { key: "Escape" });
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  await waitFor(() => expect(document.activeElement).toBe(open));
});
