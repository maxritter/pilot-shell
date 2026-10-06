// @vitest-environment happy-dom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { LoadedShare } from "@/lib/sharing/sharing";
import { SharedLink } from "./Shared";

vi.mock("@/lib/sharing/sharing", async (original) => {
  const actual = await original<typeof import("@/lib/sharing/sharing")>();
  return { ...actual, loadShare: vi.fn(async () => ready()), readShareUpdate: vi.fn() };
});
import { readShareUpdate } from "@/lib/sharing/sharing";

const ready = (title = "ql-verify-before"): Extract<LoadedShare, { status: "ready" }> => ({
  status: "ready", kind: "v2", title, docs: { "02-plan.md": `# ${title}` }, items: [],
});
const loaded = (rev: number, state = ready()) => ({ kind: "loaded", rev, state });
const flush = async (ms = 0) => act(async () => { await vi.advanceTimersByTimeAsync(ms); });

beforeEach(() => {
  vi.useFakeTimers();
  vi.mocked(readShareUpdate).mockReset();
  Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
});
afterEach(() => { cleanup(); vi.useRealTimers(); });

describe("an open share follows its owner", () => {
  it("bounds missed revision bumps with a full look, without exposing the key to the loader's URL", async () => {
    vi.mocked(readShareUpdate).mockResolvedValueOnce(loaded(7) as never).mockResolvedValue({ kind: "unchanged" } as never);
    render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await flush();
    await flush(30_000);
    expect(vi.mocked(readShareUpdate).mock.calls[1]?.[2]).toBe(7);
    await flush(870_000);
    expect(vi.mocked(readShareUpdate).mock.calls[30]?.[2]).toBeUndefined();
  });

  it("does not overlap a slow request, times it out, and backs off before trying again", async () => {
    vi.mocked(readShareUpdate).mockImplementationOnce(async (_id, _key, _since, _fetch, signal) => new Promise((resolve) => {
      signal?.addEventListener("abort", () => resolve({ kind: "retry", message: "timed out" }), { once: true });
    }));
    vi.mocked(readShareUpdate).mockResolvedValue(loaded(2) as never);
    render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await flush(44_999);
    expect(readShareUpdate).toHaveBeenCalledTimes(1);
    await flush(1);
    expect(readShareUpdate).toHaveBeenCalledTimes(2);
  });

  it("updates the five steps and Plan still without remounting the guest's draft", async () => {
    vi.mocked(readShareUpdate).mockResolvedValueOnce(loaded(1) as never);
    const { unmount } = render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await flush();
    fireEvent.change(screen.getByRole("textbox", { name: "Comment" }), { target: { value: "ql-verify-draft" } });
    const docs = Object.fromEntries(["01-discuss.md", "02-plan.md", "03-implement.md", "04-verify.md", "05-review.md"].map((name) => [name, `# ql-verify-latest-${name}`]));
    docs["02-plan.md"] += "\n\n```artifact\ndesign/settings.html\n```";
    vi.mocked(readShareUpdate).mockResolvedValueOnce(loaded(2, { ...ready("ql-verify-after"), docs, stills: { "design/settings.html": { title: "ql-verify-settings", image: "data:image/png;base64,iVBORw0KGgo=" } } } as never) as never);
    await flush(30_000);
    expect(screen.getAllByText("ql-verify-after").length).toBeGreaterThan(0);
    expect((screen.getByRole("textbox", { name: "Comment" }) as HTMLTextAreaElement).value).toBe("ql-verify-draft");
    expect((screen.getByRole("img", { name: "ql-verify-settings" }) as HTMLImageElement).src).toBe("data:image/png;base64,iVBORw0KGgo=");
    for (const step of ["Discuss", "Plan", "Implement", "Verify", "Review"]) expect(screen.getByRole("button", { name: step })).toBeTruthy();
    unmount();
    await flush(300_000);
    expect(readShareUpdate).toHaveBeenCalledTimes(2);
  });

  it("pauses hidden tabs, resumes visible ones, and respects Retry-After across visibility changes", async () => {
    vi.mocked(readShareUpdate).mockResolvedValue(loaded(1) as never);
    render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await flush();
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
    await act(async () => { document.dispatchEvent(new Event("visibilitychange")); });
    await flush(120_000);
    expect(readShareUpdate).toHaveBeenCalledTimes(1);
    vi.mocked(readShareUpdate).mockResolvedValueOnce({ kind: "retry", retryAfter: 120_000, message: "busy" } as never);
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
    await act(async () => { document.dispatchEvent(new Event("visibilitychange")); });
    await flush();
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
    await act(async () => { document.dispatchEvent(new Event("visibilitychange")); });
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
    await act(async () => { document.dispatchEvent(new Event("visibilitychange")); });
    await flush(119_999);
    expect(readShareUpdate).toHaveBeenCalledTimes(2);
    await flush(1);
    expect(readShareUpdate).toHaveBeenCalledTimes(3);
  });

  it("backs off failures, keeps the last page and draft, and clears a revoked link", async () => {
    vi.mocked(readShareUpdate).mockResolvedValueOnce(loaded(1) as never);
    render(<SharedLink id={"A".repeat(22)} linkKey={"B".repeat(43)} />);
    await flush();
    fireEvent.change(screen.getByRole("textbox", { name: "Comment" }), { target: { value: "ql-verify-kept" } });
    vi.mocked(readShareUpdate).mockResolvedValue({ kind: "retry", message: "offline" } as never);
    await flush(30_000);
    await flush(30_000);
    await flush(59_999);
    expect(readShareUpdate).toHaveBeenCalledTimes(3);
    expect((screen.getByRole("textbox", { name: "Comment" }) as HTMLTextAreaElement).value).toBe("ql-verify-kept");
    vi.mocked(readShareUpdate).mockResolvedValueOnce({ kind: "loaded", state: { status: "gone" } } as never);
    await flush(1);
    expect(screen.getByText("This plan is no longer shared")).toBeTruthy();
    await flush(300_000);
    expect(readShareUpdate).toHaveBeenCalledTimes(4);
  });
});
