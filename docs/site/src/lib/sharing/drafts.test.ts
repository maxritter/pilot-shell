import { describe, expect, it } from "vitest";
import { addRemark, answerItem, EMPTY, pending, removeRemark, summary } from "./drafts";
import type { ShareItem } from "./sharing";

/** What a link reviewer has written but not sent: answers to the owner's questions and comments. */

const item = (id: string, over: Partial<ShareItem> = {}): ShareItem => ({
  id,
  step: "plan",
  family: "decide",
  kind: "decision",
  kindLabel: "Engineering decision",
  what: `What ${id}`,
  options: ["agree", "change"],
  ...over,
});

const DOCS = { "01-discuss.md": "d", "02-plan.md": "p" };
const ITEMS = [item("a"), item("b", { family: "look", kind: "mockup", kindLabel: "Mockup" }), item("c")];

describe("answers to the owner's questions", () => {
  it("counts an agreement at once, and a change or a reply only once it says something", () => {
    let d = answerItem(EMPTY, "a", "agree");
    expect(summary(d, ITEMS)).toEqual({ answered: 1, total: 3, comments: 0 });
    d = answerItem(d, "b", "change");
    expect(summary(d, ITEMS).answered).toBe(1);
    d = answerItem(d, "b", "change", "Make the tabs wider");
    expect(summary(d, ITEMS).answered).toBe(2);
  });

  it("lets an answer be changed or taken back until it is sent", () => {
    let d = answerItem(EMPTY, "a", "agree");
    d = answerItem(d, "a", "change", "No");
    expect(d.answers.a).toEqual({ answer: "change", note: "No" });
    d = answerItem(d, "a", null);
    expect(d.answers).toEqual({});
  });

  it("sends the answers in the order the questions are asked, before the comments", () => {
    let d = addRemark(EMPTY, { kind: "passage", doc: "02-plan.md", quote: "", text: "General remark" });
    d = answerItem(d, "c", "agree");
    d = answerItem(d, "a", "change", "Rename it");
    expect(pending(d, ITEMS, DOCS).map((r) => r.kind)).toEqual(["item", "item", "passage"]);
    expect(pending(d, ITEMS, DOCS)[0]).toMatchObject({ kind: "item", id: "a", answer: "change", note: "Rename it" });
    expect(pending(d, ITEMS, DOCS)[1]).toMatchObject({ kind: "item", id: "c", answer: "agree" });
  });

  it("sends nothing for a change that says nothing, and nothing for a question that is gone", () => {
    let d = answerItem(EMPTY, "a", "change");
    d = answerItem(d, "gone", "agree");
    expect(pending(d, ITEMS, DOCS)).toEqual([]);
  });
});

describe("comments", () => {
  it("counts the comments apart from the answers and lets one be removed", () => {
    let d = addRemark(EMPTY, { kind: "passage", doc: "02-plan.md", quote: "One", text: "Why?" });
    d = addRemark(d, { kind: "thread", thread: "g-1", anchor: { kind: "doneMeans", id: "1" }, text: "Proof?" });
    expect(summary(d, ITEMS)).toEqual({ answered: 0, total: 3, comments: 2 });
    d = removeRemark(d, 0);
    expect(d.remarks).toEqual([{ kind: "thread", thread: "g-1", anchor: { kind: "doneMeans", id: "1" }, text: "Proof?" }]);
  });

  it("drops a comment with no words", () => {
    expect(addRemark(EMPTY, { kind: "passage", doc: "x", quote: "", text: "   " })).toBe(EMPTY);
  });
});
