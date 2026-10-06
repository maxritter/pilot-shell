// @vitest-environment happy-dom
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { LoadedShare, Remark } from "@/lib/sharing/sharing";
import * as sharing from "@/lib/sharing/sharing";
import { SharedLink, SharedView } from "./Shared";

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.useRealTimers(); localStorage.clear(); });
const seen = (text: string) => screen.queryAllByText(text).length > 0;
const sendButton = () => screen.getAllByRole("button", { name: "Send to Max" })[0] as HTMLButtonElement;
const state: Extract<LoadedShare, { status: "ready" }> = {
  status: "ready", kind: "v2", title: "Settings cleanup", owner: "Max", stage: "plan",
  docs: { "02-plan.md": "# The Plan\n\nOne deployment." }, items: [],
};
function addComment(text = "Why one?") {
  fireEvent.change(screen.getByLabelText("Your name"), { target: { value: "Gina" } });
  fireEvent.change(screen.getByRole("textbox", { name: "Comment" }), { target: { value: text } });
  fireEvent.click(screen.getByRole("button", { name: "Add comment" }));
}

describe("commenting on the five documents", () => {
  it("files the comment on its own step document, without an approval vote", async () => {
    const onSend = vi.fn(async (_author: string, _remarks: Remark[]) => ({ ok: true as const }));
    render(<SharedView state={state} onSend={onSend} />);
    expect(sendButton().disabled).toBe(true);
    addComment();
    expect(seen("1 comment")).toBe(true);
    fireEvent.click(sendButton());
    await waitFor(() => expect(onSend).toHaveBeenCalledTimes(1));
    expect(onSend.mock.calls[0]).toEqual(["Gina", [{ kind: "passage", doc: "02-plan.md", quote: "", text: "Why one?" }]]);
    expect(JSON.stringify(onSend.mock.calls)).not.toMatch(/verdict|approve|request_changes/);
    expect(seen("Sent to Max.")).toBe(true);
  });

  it("keeps unsent comments for another try when the owner cannot be reached", async () => {
    render(<SharedView state={state} onSend={async () => ({ ok: false, reason: "network" })} />);
    addComment();
    fireEvent.click(sendButton());
    await screen.findByRole("alert");
    expect(screen.getByRole("alert").textContent).toContain("could not be sent");
    expect(seen("1 comment")).toBe(true);
    expect(seen("Sent to Max.")).toBe(false);
  });
});

describe("keeping an open link current", () => {
  it("refreshes without losing comments, keeps the page through an outage, and hides a revoked link", async () => {
    vi.useFakeTimers();
    vi.spyOn(document, "visibilityState", "get").mockReturnValue("visible");
    const load = vi.spyOn(sharing, "readShareUpdate").mockResolvedValue({ kind: "loaded", state, rev: 1 });
    await act(async () => { render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />); });
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
    addComment();
    load.mockResolvedValue({ kind: "loaded", state: { ...state, docs: { "02-plan.md": "# Latest Plan\n\nThe Plan changed." } }, rev: 2 });
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(seen("The Plan changed.")).toBe(true);
    expect(seen("1 comment")).toBe(true);
    load.mockResolvedValue({ kind: "retry", message: "Temporary outage" });
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(seen("The Plan changed.")).toBe(true);
    expect(seen("1 comment")).toBe(true);
    expect(seen("Updates could not be received. Showing the last version until the connection returns.")).toBe(true);
    load.mockResolvedValue({ kind: "loaded", state: { status: "gone" } });
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(seen("The Plan changed.")).toBe(false);
    expect(load).toHaveBeenCalledTimes(4);
  });

  it("makes no background reads while hidden and clears its timer on unmount", async () => {
    vi.useFakeTimers();
    const visibility = vi.spyOn(document, "visibilityState", "get").mockReturnValue("hidden");
    const load = vi.spyOn(sharing, "readShareUpdate").mockResolvedValue({ kind: "loaded", state, rev: 1 });
    const view = render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await act(async () => { await Promise.resolve(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(120_000); });
    expect(load).not.toHaveBeenCalled();
    visibility.mockReturnValue("visible");
    await act(async () => {
      fireEvent(document, new Event("visibilitychange"));
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(load).toHaveBeenCalledTimes(1);
    view.unmount();
    expect(vi.getTimerCount()).toBe(0);
  });
});
