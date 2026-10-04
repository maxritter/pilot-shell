// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { type LoadedShare, parseItems, type Remark } from "@/lib/sharing/sharing";
import { SharedView } from "./Shared";

/**
 * A link reviewer at work in a real DOM: they pick answers, write a note, send, and the page
 * hands exactly their answers to the sender, with no vote, and shows what was sent.
 */

afterEach(cleanup);

/** The text is on the page; below 900 px the sticky bar repeats the count and the Send button, so there may be two. */
const seen = (text: string) => screen.queryAllByText(text).length > 0;
const sendButton = () => screen.getAllByRole("button", { name: "Send to Max" })[0] as HTMLButtonElement;

const state: Extract<LoadedShare, { status: "ready" }> = {
  status: "ready",
  kind: "v2",
  title: "Settings cleanup",
  owner: "Max",
  docs: { "02-plan.md": "# The Plan\n\nOne Vercel deployment." },
  items: parseItems([
    { id: "plan:look", step: "plan", family: "look", kind: "mockup", kindLabel: "Mockup", what: "Settings after the change", answers: { options: ["agree", "change"] } },
    { id: "plan:flow", step: "plan", family: "decide", kind: "decision", kindLabel: "Engineering decision", what: "The second opinion follows the Plan's risk", answers: { options: ["agree", "change"] } },
    { id: "plan:scope", step: "plan", family: "decide", kind: "scope", kindLabel: "Out of scope", what: "No migration of old memories", answers: { options: ["agree", "change"] } },
  ]),
};

describe("answering the owner's questions and sending", () => {
  it("sends the answers and the note as one batch with no verdict, then shows them as sent", async () => {
    const onSend = vi.fn(async (_author: string, _remarks: Remark[]) => ({ ok: true as const }));
    render(<SharedView state={state} onSend={onSend} />);

    expect(seen("0 of 3 answered · 0 comments")).toBe(true);
    const send = sendButton();
    expect(send.disabled).toBe(true);

    fireEvent.click(screen.getByRole("button", { name: "Looks right" }));
    fireEvent.click(screen.getAllByRole("button", { name: "Suggest a change" })[1] as HTMLElement);
    // A change counts once it says what should change.
    expect(seen("1 of 3 answered · 0 comments")).toBe(true);
    fireEvent.change(screen.getByLabelText("What should change?"), { target: { value: "Only on risky Plans" } });
    expect(seen("2 of 3 answered · 0 comments")).toBe(true);
    fireEvent.change(screen.getByLabelText("Your name"), { target: { value: "Gina" } });

    expect(send.disabled).toBe(false);
    fireEvent.click(send);

    await waitFor(() => expect(onSend).toHaveBeenCalledTimes(1));
    const [author, remarks] = onSend.mock.calls[0] as [string, Remark[]];
    expect(author).toBe("Gina");
    expect(remarks).toEqual([
      expect.objectContaining({ kind: "item", id: "plan:look", answer: "agree", label: "Looks right", note: "" }),
      expect.objectContaining({ kind: "item", id: "plan:flow", answer: "change", label: "Suggest a change", note: "Only on risky Plans" }),
    ]);
    // A link reviewer sends comments only: nothing in what leaves is a verdict.
    expect(JSON.stringify(remarks)).not.toMatch(/verdict|approve|request_changes/i);

    // The answered questions are settled and still counted; the one left is still open.
    await screen.findByText("You answered: Looks right. Sent.");
    expect(screen.getByText("You answered: Suggest a change. Sent.")).toBeTruthy();
    expect(seen("2 of 3 answered · 0 comments")).toBe(true);
    expect(screen.getByText("Sent to Max.")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "Agree" })).toHaveLength(1);
    expect(sendButton().disabled).toBe(true);
  });

  it("keeps everything for another try when the owner cannot be reached, and says why", async () => {
    const onSend = vi.fn(async () => ({ ok: false as const, reason: "network" as const }));
    render(<SharedView state={state} onSend={onSend} />);
    fireEvent.click(screen.getAllByRole("button", { name: "Agree" })[0] as HTMLElement);
    fireEvent.click(sendButton());
    await screen.findByRole("alert");
    expect(screen.getByRole("alert").textContent).toContain("could not be sent");
    expect(seen("1 of 3 answered · 0 comments")).toBe(true);
    expect(screen.queryByText("Sent to Max.")).toBeNull();
  });

  it("files a comment on the passage's own document, and sends it with the answers", async () => {
    const onSend = vi.fn(async (_author: string, _remarks: Remark[]) => ({ ok: true as const }));
    render(<SharedView state={state} onSend={onSend} />);
    fireEvent.change(screen.getByRole("textbox", { name: "Comment" }), { target: { value: "Why one?" } });
    fireEvent.click(screen.getByRole("button", { name: "Add comment" }));
    expect(seen("0 of 3 answered · 1 comment")).toBe(true);
    fireEvent.click(sendButton());
    await waitFor(() => expect(onSend).toHaveBeenCalledTimes(1));
    expect(onSend.mock.calls[0]?.[1]).toEqual([{ kind: "passage", doc: "02-plan.md", quote: "", text: "Why one?" }]);
  });
});
