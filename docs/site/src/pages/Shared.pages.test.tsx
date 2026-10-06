// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { LoadedShare } from "@/lib/sharing/sharing";
import { SharedView } from "./Shared";

afterEach(cleanup);
const state = (docs: Record<string, string>, stage = "review"): Extract<LoadedShare, { status: "ready" }> => ({
  status: "ready", kind: "v2", title: "A shared task", docs, items: [], stage,
} as Extract<LoadedShare, { status: "ready" }>);

describe("the five public step pages", () => {
  it("opens each of the five documents under its own step", () => {
    render(<SharedView state={state({ "01-discuss.md": "Discuss body", "02-plan.md": "Plan body", "03-implement.md": "Implement body", "04-verify.md": "Verify body", "05-review.md": "Review body" })} onSend={async () => ({ ok: true })} />);
    for (const label of ["Discuss", "Plan", "Implement", "Verify", "Review"]) {
      fireEvent.click(screen.getByRole("button", { name: label }));
      expect(screen.getByText(`${label} body`)).toBeTruthy();
    }
    expect(screen.queryByRole("button", { name: "Build" })).toBeNull();
  });

  it("a future step says not started and a task without a design has no mockup section", () => {
    render(<SharedView state={state({ "01-discuss.md": "Discuss body", "02-plan.md": "Plan body" }, "plan")} onSend={async () => ({ ok: true })} />);
    fireEvent.click(screen.getByRole("button", { name: "Verify" }));
    expect(screen.getByText("Verify has not started yet.")).toBeTruthy();
    expect(screen.queryByTestId("shared-mockup")).toBeNull();
    expect(screen.queryByTestId("shared-mockup-missing")).toBeNull();
  });
});
