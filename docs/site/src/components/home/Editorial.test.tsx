// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
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
