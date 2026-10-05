import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it, vi } from "vitest";
import fixture from "@/lib/sharing/shared-review.fixture.json";
import { checkId, type LoadedShare, linkKeyOf, loadShare, openFromLink, parseItems, parseReview, sealForLink } from "@/lib/sharing/sharing";
import { SharedView } from "./Shared";

/**
 * The page a link opens: the plan is sealed with a key that only the link's fragment carries, so
 * the page opens it in the browser and seals each comment with the same key. A link without its
 * key says so, and "no longer shared" is for a link that is gone. A link reviewer reads Discuss,
 * Plan and Build, answers the owner's questions and comments; they never vote.
 */

const V2_ID = "A".repeat(22);
const OLD_DOCS = { "README.md": "# Task\n\nThe problem.", "02-design.md": "# Design\n\nOne Vercel deployment." };
const KEY = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(32))))
  .replace(/\+/g, "-")
  .replace(/\//g, "_")
  .replace(/=+$/, "");

const answer = (status: number, body?: unknown) =>
  vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })) as unknown as typeof fetch;

/** What the backend serves for a link: the plan sealed with the link's key, as the owner's machine seals it. */
const sealedShare = async (plan: Record<string, unknown>, expires?: string, key = KEY) =>
  answer(200, { ...(await sealForLink(key, "plan", JSON.stringify(plan))), ...(expires !== undefined ? { expires } : {}) });

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

describe("loading a link", () => {
  it("opens a sealed plan with the key from the link: its documents and expiry", async () => {
    const fetchFn = await sealedShare({ task: "Pager off-by-one", docs: OLD_DOCS }, "2026-10-14T10:00:00.000Z");
    const loaded = await loadShare(V2_ID, KEY, fetchFn);
    expect(loaded).toEqual({
      status: "ready",
      kind: "v2",
      title: "Pager off-by-one",
      docs: OLD_DOCS,
      items: [],
      expires: "2026-10-14T10:00:00.000Z",
    });
    expect(fetchFn).toHaveBeenCalledWith(`/api/share?id=${V2_ID}`);
  });

  it("says a link without its key is missing it, and never asks the server", async () => {
    const never = answer(200, {});
    expect(await loadShare(V2_ID, "", never)).toEqual({ status: "no-key" });
    expect(never).not.toHaveBeenCalled();
  });

  it("reads the key from the fragment only when it has the shape of one", () => {
    expect(linkKeyOf(`#${KEY}`)).toBe(KEY);
    expect(linkKeyOf("")).toBe("");
    expect(linkKeyOf("#short")).toBe("");
    expect(linkKeyOf(`#${KEY}x`)).toBe("");
  });

  it("does not open a plan sealed with another key, or one the server left in plain text", async () => {
    const other = await sealedShare({ task: "Pager off-by-one", docs: OLD_DOCS }, undefined, "B".repeat(43));
    expect(await loadShare(V2_ID, KEY, other)).toMatchObject({ status: "error" });
    expect(await loadShare(V2_ID, KEY, answer(200, { v: 2, task: "Pager off-by-one", docs: OLD_DOCS }))).toMatchObject({ status: "error" });
  });

  it("opens only what the seal says it is: a comment's seal is not a plan", async () => {
    const asComment = await sealForLink(KEY, "feedback", JSON.stringify({ task: "Pager off-by-one", docs: OLD_DOCS }));
    expect(await openFromLink(KEY, "plan", asComment)).toBeNull();
    expect(await loadShare(V2_ID, KEY, answer(200, asComment))).toMatchObject({ status: "error" });
  });

  it("says a revoked or expired link is gone, and a damaged or unreachable one is an error", async () => {
    expect(await loadShare(V2_ID, KEY, answer(404, { error: "Share not found or expired" }))).toEqual({ status: "gone" });
    expect(await loadShare(V2_ID, KEY, answer(500))).toMatchObject({ status: "error" });
    expect(await loadShare(V2_ID, KEY, answer(200, { data: "not-a-payload" }))).toMatchObject({ status: "error" });
    const offline = vi.fn(async () => {
      throw new Error("offline");
    }) as unknown as typeof fetch;
    expect(await loadShare(V2_ID, KEY, offline)).toMatchObject({ status: "error" });
    // An id of the wrong shape never reaches the network.
    const never = answer(200, {});
    expect(await loadShare("short", KEY, never)).toMatchObject({ status: "error" });
    expect(never).not.toHaveBeenCalled();
  });
});

type Ready = Extract<LoadedShare, { status: "ready" }>;

const ready = (over: Partial<Ready> = {}): Ready => ({ status: "ready", kind: "v2", title: "Settings cleanup", docs: {}, items: [], ...over });

const MOCKUP = "<!doctype html><title>Settings</title><h1>Settings</h1><script>parent.postMessage({type:'x'},'*')</script>";

/** A task as the App shares it once the Plan waits: the five step files, the mockup, the owner's questions. */
const PLAN_SHARE = ready({
  owner: "Max",
  expires: "2026-10-18T10:00:00.000Z",
  docs: {
    "00-discuss.md": "# Problem\n\nSettings are too many.",
    "01-research.md": "# Research\n\nSECRET RESEARCH NOTES",
    "02-plan.md": [
      "# Fewer settings",
      "",
      "First the configuration changes.",
      "",
      "```artifact",
      "artifacts/settings.html",
      "```",
      "",
      "```mermaid",
      "graph LR; Config-->Flow",
      "```",
    ].join("\n"),
    "02-plan-details.md": [
      "## System design contracts",
      "",
      "### The flow stops reading the config",
      "",
      "A contract body.",
      "",
      "### A 429 keeps the error shape",
      "",
      "Another body.",
      "",
      "## Slice 1: Fewer settings, in the CLI and the App together",
      "",
      "- [ ] T1 One",
      "- [ ] T2 Two",
      "",
      "## Slice 2: Select all fills a group",
      "",
      "- [ ] T3 Three",
    ].join("\n"),
    "artifacts/settings.html": MOCKUP,
  },
  items: parseItems([
    { id: "plan:mockup:1", step: "plan", family: "look", kind: "mockup", kindLabel: "Mockup", what: "Settings after the change", answers: { options: ["agree", "change"] }, media: { kind: "artifact", name: "settings.html" } },
    { id: "plan:decision:1", step: "plan", family: "decide", kind: "decision", kindLabel: "Engineering decision", what: "The flow stops reading the config", answers: { options: ["agree", "change"] } },
    { id: "plan:scope:1", step: "plan", family: "decide", kind: "scope", kindLabel: "Out of scope", what: "No migration of old memories", answers: { options: ["agree", "change"] } },
  ]),
});

const noSend = async () => ({ ok: true as const });

describe("the page for a task at the Plan", () => {
  it("names its tabs for the steps, never for files, and says nothing of research", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("Settings cleanup");
    for (const tab of [">Discuss<", ">Plan<", ">Build<"]) expect(page).toContain(tab);
    // What a reader sees, not the attributes the page keeps for itself.
    const seen = page.replace(/<[^>]*>/g, " ");
    for (const file of ["00-discuss", "02-plan", "02-plan-details", "01-research", "README", ".md"]) expect(seen).not.toContain(file);
    expect(page).not.toContain("SECRET RESEARCH");
    expect(page).not.toContain(">Research<");
  });

  it("opens on the Plan, and says how long the link lives and that no code is shared", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("First the configuration changes.");
    expect(page).toContain("Max shared this with you to read and comment on");
    expect(page).toContain("the link runs out on");
    expect(page).toContain("no code is shared");
  });

  it("shows the mockup as a page in a sandboxed frame of its own, not as its file path", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("<iframe");
    // The frame is the static page with its own header policy; the mockup reaches it by message, not by srcdoc.
    expect(page).toContain('src="/s-frame.html"');
    expect(page).not.toContain("srcDoc");
    expect(page).not.toContain("srcdoc");
    expect(page).toContain('sandbox="allow-scripts"');
    expect(page).not.toContain("allow-same-origin");
    expect(page).not.toContain("artifacts/settings.html");
    expect(page).not.toContain("settings.html");
  });

  it("draws a mockup once when the plan's fence and a question name the same file", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page.split("<iframe").length - 1).toBe(1);
    // With no question for it, the fence draws it where the plan put it.
    const bare = await html(<SharedView state={{ ...PLAN_SHARE, items: [] }} onSend={noSend} />);
    expect(bare.split("<iframe").length - 1).toBe(1);
  });

  it("draws the diagram where the plan has it, and keeps its source until it is drawn", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain('data-testid="shared-diagram"');
    expect(page).toContain("Config--&gt;Flow");
  });

  it("includes the slices with their task counts, and the contracts behind a fold", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("The build");
    expect(page).toContain("2 slices, 3 tasks");
    expect(page).toContain("Fewer settings, in the CLI and the App together");
    expect(page).toContain("Select all fills a group");
    expect(page).toContain("2 tasks");
    expect(page).toContain("1 task<");
    expect(page).toContain("Contracts");
    expect(page).toContain("2 interfaces");
    expect(page).toContain("The flow stops reading the config");
    expect(page).toContain("A 429 keeps the error shape");
  });

  it("shows the questions the owner asks, each with the App's answers", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("Max asks you");
    expect(page).toContain("3 questions");
    expect(page).toContain("your answers reach Max as comments");
    expect(page).toContain("Mockup");
    expect(page).toContain("Settings after the change");
    expect(page).toContain("Engineering decision");
    expect(page).toContain("Out of scope");
    expect(page).toContain(">Looks right<");
    expect(page).toContain(">Agree<");
    expect(page).toContain(">Suggest a change<");
  });

  it("lets a link reviewer comment and nothing more: a name, Send to the owner, no Approve, no Request changes", async () => {
    const page = await html(<SharedView state={PLAN_SHARE} onSend={noSend} />);
    expect(page).toContain("Your name");
    expect(page).toContain("No account needed");
    expect(page).toContain(">Send to Max<");
    expect(page).toContain("Approving is for Max&#x27;s team, in the App.");
    expect(page).not.toContain("Request changes");
    expect(page).not.toContain(">Approve<");
    expect(page).not.toContain("Approved");
    expect(page).toContain("0 of 3 answered");
  });

  it("names the owner when the link does not say who it is", async () => {
    const page = await html(<SharedView state={{ ...PLAN_SHARE, owner: undefined }} onSend={noSend} />);
    expect(page).toContain(">Send to the owner<");
    expect(page).toContain("The owner asks you");
  });

  it("shows Discuss as its own step, and a step not reached says what will happen there", async () => {
    const discuss = await html(<SharedView state={PLAN_SHARE} onSend={noSend} tab="discuss" />);
    expect(discuss).toContain("Settings are too many.");
    const build = await html(<SharedView state={PLAN_SHARE} onSend={noSend} tab="build" />);
    expect(build).toContain("The build has not started");
    expect(build).not.toContain("Settings are too many.");
  });

  it("reads a new task's files: Discuss from 01-discuss.md, and none of the agent's own files", async () => {
    const { "00-discuss.md": _old, "01-research.md": _research, ...kept } = PLAN_SHARE.docs;
    const docs = {
      ...kept,
      "01-discuss.md": "# Problem\n\nSettings are too many, said the new task.",
      "01-discuss-details.md": "# Details\n\nSECRET DISCUSS DETAILS",
      "01-discuss-research.md": "# Research\n\nSECRET RESEARCH NOTES",
    };
    const state = { ...PLAN_SHARE, docs };
    const discuss = await html(<SharedView state={state} onSend={noSend} tab="discuss" />);
    expect(discuss).toContain("said the new task.");
    const plan = await html(<SharedView state={state} onSend={noSend} />);
    for (const page of [discuss, plan]) {
      expect(page).not.toContain("SECRET");
      // What a reader sees, not the attributes the page keeps for itself.
      expect(page.replace(/<[^>]*>/g, " ")).not.toContain("01-discuss");
    }
  });
});

describe("a link made before the App sent steps, items and the owner's name", () => {
  it("still opens: the frame is Discuss, the design is the Plan, and the page asks nothing", async () => {
    const state = ready({ title: "Pager off-by-one", docs: OLD_DOCS, expires: "2026-10-14T10:00:00.000Z" });
    const plan = await html(<SharedView state={state} onSend={noSend} />);
    expect(plan).toContain("One Vercel deployment");
    for (const tab of [">Discuss<", ">Plan<", ">Build<"]) expect(plan).toContain(tab);
    expect(plan).not.toContain(">README<");
    expect(plan).not.toContain(">02-design<");
    expect(plan).not.toContain("asks you");
    expect(plan).toContain(">Send to the owner<");
    const discuss = await html(<SharedView state={state} onSend={noSend} tab="discuss" />);
    expect(discuss).toContain("The problem.");
  });

  it("says a link that is gone is no longer shared", async () => {
    const page = await html(<SharedView state={{ status: "gone" }} onSend={noSend} />);
    expect(page).toContain("This plan is no longer shared");
    expect(page).not.toContain("Send to");
  });

  it("says a link without its key is missing it, and offers no comment box", async () => {
    const page = await html(<SharedView state={{ status: "no-key" }} onSend={noSend} />);
    expect(page).toContain("This link is missing its key");
    expect(page).not.toContain("Send to");
  });
});

/**
 * A link reviewer and the finished change: the App's SharedReview arrives as
 * docs["review.json"] (fixture from the build session, 625ceb66). They read Overview,
 * Evidence and Try it under Build, and comment; they never vote or see the files.
 */
describe("the shared change, under Build", () => {
  const REVIEW = JSON.stringify(fixture);

  it("reads the change from review.json and keeps it out of the documents", async () => {
    const loaded = await loadShare(V2_ID, KEY, await sealedShare({ task: "Rate-limit the export API", docs: { ...OLD_DOCS, "review.json": REVIEW } }));
    expect(loaded.status === "ready" && Object.keys(loaded.docs)).toEqual(["README.md", "02-design.md"]);
    expect(loaded.status === "ready" && loaded.review?.doneMeans[0]?.head).toBe("A 61st export in an hour is refused with a retry time.");
  });

  it("ignores a malformed change and keeps only inline images", () => {
    expect(parseReview("not json")).toBeUndefined();
    expect(parseReview(JSON.stringify({ verified: true }))).toBeUndefined();
    const review = parseReview(JSON.stringify({ ...fixture, images: { "a.png": "data:image/png;base64,AA", "b.png": "https://example.com/b.png" } }));
    expect(Object.keys(review?.images ?? {})).toEqual(["a.png"]);
  });

  it("opens on Build once the change is verified: its proofs, the pull request and the tabs, with comments but no vote", async () => {
    const review = parseReview(REVIEW);
    const page = await html(<SharedView state={ready({ title: "Rate-limit the export API", docs: OLD_DOCS, review })} onSend={noSend} />);
    expect(page).toContain("A 61st export in an hour is refused with a retry time.");
    expect(page).toContain("Passed");
    expect(page).toContain("#42");
    for (const tab of [">Discuss<", ">Plan<", ">Build<", ">Overview<", ">Evidence<", ">Try it<"]) expect(page).toContain(tab);
    expect(page).toContain("Add comment");
    expect(page).not.toContain("Request changes");
    expect(page).not.toContain(">Approve<");
    expect(page).not.toContain("Files changed");
    expect(page).not.toContain("round");
  });

  it("anchors a check the way the App does", () => {
    expect(checkId("scenario 1")).toBe("scenario:1");
    expect(checkId("dod T3")).toBe("dod:T3");
  });
});
