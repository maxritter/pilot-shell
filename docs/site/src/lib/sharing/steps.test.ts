import { describe, expect, it, vi } from "vitest";
import { answerItem, EMPTY, pending } from "./drafts";
import {
  answerWords,
  loadShare,
  openFromLink,
  parseItems,
  remarksPayload,
  type ShareItem,
  sealForLink,
  stepDocs,
  submitRemarks,
  tabsOf,
} from "./sharing";

/**
 * What a link holds, named the way the App names it: Discuss, Plan and Build, never the files;
 * research is the agent's own and never leaves the machine; the owner's questions arrive as items.
 */

const KEY = "A".repeat(43);
const ID = "B".repeat(22);

const answer = (status: number, body?: unknown) =>
  vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })) as unknown as typeof fetch;

describe("a link's documents, by step", () => {
  it("sorts the five step files into Discuss, Plan and Build, in the order the work produced them", () => {
    const docs = {
      "03-build.md": "b",
      "02-plan-details.md": "pd",
      "02-plan.md": "p",
      "00-discuss.md": "d",
      "artifacts/settings.html": "<html></html>",
      "review.json": "{}",
    };
    expect(stepDocs(docs)).toEqual({ discuss: ["00-discuss.md"], research: [], plan: ["02-plan.md", "02-plan-details.md"], outline: [], implement: ["03-build.md"], verify: [], review: [] });
  });

  it("never lists research or a diagnosis, even when the link carries them", () => {
    const docs = { "00-discuss.md": "d", "01-research.md": "SECRET", "01-diagnosis.md": "SECRET", "02-plan.md": "p" };
    const steps = stepDocs(docs);
    expect(Object.values(steps).flat()).toEqual(["00-discuss.md", "02-plan.md"]);
  });

  it("reads a new task's Discuss and Plan: 01-discuss.md is Discuss, and the slices come from the details", () => {
    const docs = { "01-discuss.md": "d", "02-plan.md": "p", "02-plan-details.md": "pd" };
    expect(stepDocs(docs)).toEqual({ discuss: ["01-discuss.md"], research: [], plan: ["02-plan.md", "02-plan-details.md"], outline: [], implement: [], verify: [], review: [] });
  });

  it("keeps the agent's files private by name, in both layouts: research, diagnosis and Discuss's details", () => {
    const docs = {
      "01-discuss.md": "d",
      "01-discuss-research.md": "SECRET",
      "01-discuss-diagnosis.md": "SECRET",
      "01-discuss-details.md": "SECRET",
      "00-discuss.md": "d",
      "00-discuss-details.md": "SECRET",
      "01-research.md": "SECRET",
      "01-diagnosis.md": "SECRET",
      "02-plan.md": "p",
    };
    expect(Object.values(stepDocs(docs)).flat()).toEqual(["00-discuss.md", "01-discuss.md", "02-plan.md"]);
  });

  it("does not drop a document for its number: only the agent's own files are private", () => {
    expect(Object.values(stepDocs({ "01-frame.md": "f", "02-plan.md": "p" })).flat()).toEqual(["01-frame.md", "02-plan.md"]);
  });

  it("reads an old link's files too: the frame is Discuss, the design and its outline are the Plan", () => {
    expect(stepDocs({ "README.md": "r", "02-design.md": "d", "03-outline-overview.md": "o" })).toEqual({
      discuss: ["README.md"],
      research: [],
      plan: ["02-design.md", "03-outline-overview.md"],
      outline: [],
      implement: [], verify: [], review: [],
    });
  });

  it("sorts a seven-step task's files into its seven steps, each by its own name", () => {
    const docs = { "01-discuss.md": "d", "02-research.md": "r", "03-plan.md": "p", "04-outline.md": "o", "05-implement.md": "i", "06-verify.md": "v", "07-review.md": "w" };
    expect(stepDocs(docs)).toEqual({
      discuss: ["01-discuss.md"], research: ["02-research.md"], plan: ["03-plan.md"], outline: ["04-outline.md"],
      implement: ["05-implement.md"], verify: ["06-verify.md"], review: ["07-review.md"],
    });
  });

  it("reads a seven-step task's research, which is a step's own document, while an older task's research stays private", () => {
    expect(Object.values(stepDocs({ "01-discuss.md": "d", "02-research.md": "r" })).flat()).toEqual(["01-discuss.md", "02-research.md"]);
    expect(Object.values(stepDocs({ "01-discuss.md": "d", "01-research.md": "SECRET", "02-plan.md": "p" })).flat()).toEqual(["01-discuss.md", "02-plan.md"]);
  });

  it("draws seven steps for a task started with them, five for an older one, told by its files", () => {
    expect(tabsOf({ "01-discuss.md": "d" })).toHaveLength(7);
    expect(tabsOf({ "01-discuss.md": "d", "02-research.md": "r", "03-plan.md": "p" })).toHaveLength(7);
    expect(tabsOf({ "01-discuss.md": "d" }, "outline")).toHaveLength(7);
    expect(tabsOf({ "01-discuss.md": "d", "02-plan.md": "p" })).toEqual(["discuss", "plan", "implement", "verify", "review"]);
    expect(tabsOf({ "00-discuss.md": "d" })).toHaveLength(5);
  });

  it("takes research for a top-level Markdown file only: a mockup named diagnostics is a mockup", async () => {
    const docs = { "02-plan.md": "p", "artifacts/diagnostics.html": "<html></html>", "artifacts/research-board.html": "<html></html>" };
    const plan = { task: "T", docs: { ...docs, "01-research.md": "SECRET" } };
    const loaded = await loadShare(ID, KEY, answer(200, await sealForLink(KEY, "plan", JSON.stringify(plan))));
    expect(loaded.status === "ready" && Object.keys(loaded.docs).sort()).toEqual(["02-plan.md"]);
  });

  it("does not hand research to the page at all", async () => {
    const plan = { task: "T", docs: { "02-plan.md": "p", "01-research.md": "SECRET" } };
    const loaded = await loadShare(ID, KEY, answer(200, await sealForLink(KEY, "plan", JSON.stringify(plan))));
    expect(loaded.status === "ready" && Object.keys(loaded.docs)).toEqual(["02-plan.md"]);
  });
});

describe("the owner's questions", () => {
  const wire = {
    id: "plan:decision:1",
    step: "plan",
    family: "decide",
    kind: "decision",
    kindLabel: "Engineering decision",
    what: "The second opinion follows the Plan's risk",
    why: "One rule, in one place",
    answers: { options: ["agree", "change"] },
    media: { kind: "mermaid", source: "graph LR; A-->B" },
    state: "open",
    blocking: false,
  };

  it("keeps the owner but leaves questions and source in the App", async () => {
    const plan = { task: "Settings cleanup", owner: "Max", docs: { "02-plan.md": "p" }, items: [wire] };
    const loaded = await loadShare(ID, KEY, answer(200, await sealForLink(KEY, "plan", JSON.stringify(plan))));
    expect(loaded).toMatchObject({ status: "ready", owner: "Max" });
    expect(loaded.status === "ready" && loaded.items).toEqual([]);
  });

  it("is empty for a link made before the App sent any", async () => {
    const loaded = await loadShare(ID, KEY, answer(200, await sealForLink(KEY, "plan", JSON.stringify({ task: "T", docs: { "02-plan.md": "p" } }))));
    expect(loaded).toMatchObject({ status: "ready", items: [] });
    expect(loaded.status === "ready" && loaded.owner).toBeUndefined();
  });

  it("keeps only what a guest can answer: no confirmations, stops, questions or findings, no settled items, no junk", () => {
    const items = parseItems([
      wire,
      { ...wire, id: "c", family: "confirm", kind: "confirm", answers: { options: ["confirm", "record"] } },
      { ...wire, id: "stop", kind: "stop" },
      { ...wire, id: "question", kind: "question", family: "answer" },
      { ...wire, id: "teammate", kind: "teammate" },
      { ...wire, id: "finding", kind: "finding" },
      { ...wire, id: "s", state: "settled" },
      { id: "no-what" },
      "nonsense",
    ]);
    expect(items.map((i) => i.id)).toEqual(["plan:decision:1"]);
    expect(parseItems("not a list")).toEqual([]);
  });

  it("reads the App's answer names as a guest's three: agree, change, reply", () => {
    const [one] = parseItems([{ ...wire, answers: { options: ["accept", "fix", "reply"] } }]);
    expect(one?.options).toEqual(["agree", "change", "reply"]);
    const [bare] = parseItems([{ ...wire, answers: undefined }]);
    expect(bare?.options).toEqual(["agree", "change"]);
  });

  it("uses the App's words for the buttons: Looks right for a mockup, Suggest a change for any change", () => {
    const [look] = parseItems([{ ...wire, family: "look", kind: "mockup" }]);
    const [decide] = parseItems([wire]);
    expect(answerWords(look as never, "agree")).toBe("Looks right");
    expect(answerWords(decide as never, "agree")).toBe("Agree");
    expect(answerWords(decide as never, "change")).toBe("Suggest a change");
    expect(answerWords(decide as never, "reply")).toBe("Reply");
  });
});

describe("sending what a guest wrote", () => {
  const remarks = [
    { kind: "item" as const, id: "plan:decision:1", step: "plan" as const, doc: "02-plan.md", what: "The second opinion follows the Plan's risk", answer: "change" as const, label: "Suggest a change", note: "Only on risky Plans" },
    { kind: "item" as const, id: "plan:mockup:1", step: "plan" as const, doc: "02-plan.md", what: "Settings after the change", answer: "agree" as const, label: "Looks right", note: "" },
    { kind: "passage" as const, doc: "02-plan.md", quote: "One Vercel deployment", text: "Why one?" },
    { kind: "thread" as const, thread: "g-abc123", anchor: { kind: "doneMeans" as const, id: "1", quote: "A 61st export" }, text: "Is 429 right?" },
    { kind: "reply" as const, thread: "g-abc123", text: "Thanks" },
  ];

  it("puts every answer and comment in one batch, as the annotations the App already reads", () => {
    const payload = remarksPayload(" Sam ", remarks, 7);
    expect(payload).toMatchObject({ author: "Sam", createdAt: 7 });
    expect("decision" in payload).toBe(false);
    expect(payload.annotations.map((a) => [a.blockId, a.originalText === "" ? "" : a.originalText.slice(0, 1)])).toEqual([
      ["02-plan.md", "T"],
      ["02-plan.md", "S"],
      ["02-plan.md", "O"],
      ["review", "{"],
      ["review", "{"],
    ]);
    expect(payload.annotations[0]?.text).toBe("Suggest a change: Only on risky Plans");
    expect(payload.annotations[1]?.text).toBe("Looks right");
    expect(payload.annotations[2]?.text).toBe("Why one?");
    expect(JSON.parse(payload.annotations[3]?.originalText ?? "")).toEqual({
      t: "thread",
      thread: "g-abc123",
      anchor: { kind: "doneMeans", id: "1", quote: "A 61st export" },
    });
    expect(JSON.parse(payload.annotations[4]?.originalText ?? "")).toEqual({ t: "reply", thread: "g-abc123" });
  });

  it("posts an answer on Discuss against the file the shared task keeps Discuss in", () => {
    const discussItem: ShareItem = {
      id: "discuss:decision:1",
      step: "discuss",
      family: "decide",
      kind: "decision",
      kindLabel: "Decision",
      what: "Which export format",
      options: ["agree", "change"],
    };
    const drafts = answerItem(EMPTY, discussItem.id, "agree");
    const docOf = (docs: Record<string, string>) =>
      remarksPayload("Sam", pending(drafts, [discussItem], docs), 1).annotations.map((a) => a.blockId);
    expect(docOf({ "01-discuss.md": "d", "02-plan.md": "p" })).toEqual(["01-discuss.md"]);
    expect(docOf({ "00-discuss.md": "d", "02-plan.md": "p", "03-build.md": "b" })).toEqual(["00-discuss.md"]);
  });

  it("posts an answer on the build against the new task's Implement file, and an older task's build log", () => {
    const buildItem: ShareItem = {
      id: "implement:decision:1",
      step: "implement",
      family: "decide",
      kind: "decision",
      kindLabel: "Decision",
      what: "Retry the export once",
      options: ["agree", "change"],
    };
    const drafts = answerItem(EMPTY, buildItem.id, "agree");
    const docOf = (docs: Record<string, string>) =>
      remarksPayload("Sam", pending(drafts, [buildItem], docs), 1).annotations.map((a) => a.blockId);
    expect(docOf({ "01-discuss.md": "d", "02-plan.md": "p" })).toEqual(["03-implement.md"]);
    expect(docOf({ "00-discuss.md": "d", "02-plan.md": "p", "03-build.md": "b" })).toEqual(["03-build.md"]);
  });

  it("names a guest who gave no name Guest", () => {
    expect(remarksPayload("  ", [remarks[2] as never], 1).author).toBe("Guest");
  });

  it("seals the batch with the link's key and sends it once", async () => {
    const fetchFn = answer(201, { ok: true });
    expect(await submitRemarks(ID, KEY, "Sam", remarks, fetchFn)).toEqual({ ok: true });
    const calls = (fetchFn as unknown as { mock: { calls: [string, RequestInit][] } }).mock.calls;
    expect(calls).toHaveLength(1);
    const sent = JSON.parse(String(calls[0]?.[1].body)) as { id: string; payload: { v: 3; iv: string; ct: string } };
    expect(calls[0]?.[0]).toBe("/api/share/feedback");
    expect(sent.id).toBe(ID);
    expect(JSON.stringify(sent)).not.toContain("Why one?");
    const opened = JSON.parse((await openFromLink(KEY, "feedback", sent.payload)) ?? "null") as { annotations: unknown[] };
    expect(opened.annotations).toHaveLength(5);
  });

  it("sends nothing when there is nothing to send, and refuses what the owner's machine would drop", async () => {
    const never = answer(201, { ok: true });
    expect(await submitRemarks(ID, KEY, "Sam", [], never)).toEqual({ ok: true });
    const long = [{ kind: "passage" as const, doc: "02-plan.md", quote: "", text: "x".repeat(4001) }];
    expect(await submitRemarks(ID, KEY, "Sam", long, never)).toEqual({ ok: false, reason: "too_large" });
    expect(await submitRemarks(ID, KEY, "G".repeat(81), [remarks[2] as never], never)).toEqual({ ok: false, reason: "too_large" });
    expect(never).not.toHaveBeenCalled();
  });

  it("tells a revoked link, a busy connection and a long comment apart", async () => {
    const one = [remarks[2] as never];
    expect(await submitRemarks(ID, KEY, "G", one, answer(404))).toEqual({ ok: false, reason: "gone" });
    expect(await submitRemarks(ID, KEY, "G", one, answer(429))).toEqual({ ok: false, reason: "rate_limited" });
    expect(await submitRemarks(ID, KEY, "G", one, answer(413))).toEqual({ ok: false, reason: "too_large" });
    expect(await submitRemarks(ID, KEY, "G", one, answer(500))).toEqual({ ok: false, reason: "network" });
  });
});
