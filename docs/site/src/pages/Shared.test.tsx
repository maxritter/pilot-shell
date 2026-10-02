import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it, vi } from "vitest";
import fixture from "@/lib/sharing/shared-review.fixture.json";
import {
  changePayload,
  checkId,
  feedbackPayload,
  linkKeyOf,
  loadShare,
  openFromLink,
  parseReview,
  sealForLink,
  submitChangeComment,
  submitComment,
} from "@/lib/sharing/sharing";
import { SharedView } from "./Shared";

/**
 * The page a link opens: the plan is sealed with a key that only the link's fragment carries, so
 * the page opens it in the browser and seals each comment with the same key. A link without its
 * key says so, and "no longer shared" is for a link that is gone. Comments leave in v11's
 * annotation format, inside the seal.
 */

const V2_ID = "A".repeat(22);
const DOCS = { "README.md": "# Task\n\nThe problem.", "02-design.md": "# Design\n\nOne Vercel deployment." };
const KEY = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(32))))
  .replace(/\+/g, "-")
  .replace(/\//g, "_")
  .replace(/=+$/, "");

const answer = (status: number, body?: unknown) =>
  vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })) as unknown as typeof fetch;

/** What the backend serves for a link: the plan sealed with the link's key, as the owner's machine seals it. */
const sealedShare = async (plan: { task: string; docs: Record<string, string> }, expires?: string, key = KEY) =>
  answer(200, { ...(await sealForLink(key, "plan", JSON.stringify(plan))), ...(expires !== undefined ? { expires } : {}) });

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

describe("loading a link", () => {
  it("opens a sealed plan with the key from the link: its documents and expiry", async () => {
    const fetchFn = await sealedShare({ task: "Pager off-by-one", docs: DOCS }, "2026-10-14T10:00:00.000Z");
    const loaded = await loadShare(V2_ID, KEY, fetchFn);
    expect(loaded).toEqual({ status: "ready", kind: "v2", title: "Pager off-by-one", docs: DOCS, expires: "2026-10-14T10:00:00.000Z" });
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
    const other = await sealedShare({ task: "Pager off-by-one", docs: DOCS }, undefined, "B".repeat(43));
    expect(await loadShare(V2_ID, KEY, other)).toMatchObject({ status: "error" });
    expect(await loadShare(V2_ID, KEY, answer(200, { v: 2, task: "Pager off-by-one", docs: DOCS }))).toMatchObject({ status: "error" });
  });

  it("opens only what the seal says it is: a comment's seal is not a plan", async () => {
    const asComment = await sealForLink(KEY, "feedback", JSON.stringify({ task: "Pager off-by-one", docs: DOCS }));
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

describe("the page", () => {
  const noComment = async () => ({ ok: true as const });

  it("shows a v2 plan: its title, each document by name, and the first one's text", async () => {
    const page = await html(
      <SharedView
        state={{ status: "ready", kind: "v2", title: "Pager off-by-one", docs: DOCS, expires: "2026-10-14T10:00:00.000Z" }}
        onComment={noComment}
      />,
    );
    expect(page).toContain("Pager off-by-one");
    expect(page).toContain(">README<");
    expect(page).toContain(">02-design<");
    expect(page).toContain("The problem.");
    expect(page).toContain("anyone who has it can read this plan and comment");
  });

  it("shows a plan with one document without tabs", async () => {
    const page = await html(
      <SharedView
        state={{ status: "ready", kind: "v2", title: "Pager off-by-one", docs: { "README.md": "# Task\n\nOnly the frame." } }}
        onComment={noComment}
      />,
    );
    expect(page).toContain("Only the frame.");
    expect(page).not.toContain('aria-label="Documents"');
  });

  it("says a link that is gone is no longer shared", async () => {
    const page = await html(<SharedView state={{ status: "gone" }} onComment={noComment} />);
    expect(page).toContain("This plan is no longer shared");
    expect(page).not.toContain("Add comment");
  });

  it("says a link without its key is missing it, and offers no comment box", async () => {
    const page = await html(<SharedView state={{ status: "no-key" }} onComment={noComment} />);
    expect(page).toContain("This link is missing its key");
    expect(page).not.toContain("Add comment");
  });
});

/**
 * A link reviewer and the finished change: the Cockpit's SharedReview arrives as
 * docs["review.json"] (fixture from the build session, 625ceb66). They read Overview,
 * Evidence and Try it, and comment; they never vote or see the files.
 */
describe("the shared change", () => {
  const REVIEW = JSON.stringify(fixture);
  const noComment = async () => ({ ok: true as const });

  it("reads the change from review.json and keeps it out of the documents", async () => {
    const loaded = await loadShare(V2_ID, KEY, await sealedShare({ task: "Rate-limit the export API", docs: { ...DOCS, "review.json": REVIEW } }));
    expect(loaded.status === "ready" && Object.keys(loaded.docs)).toEqual(["README.md", "02-design.md"]);
    expect(loaded.status === "ready" && loaded.review?.doneMeans[0]?.head).toBe("A 61st export in an hour is refused with a retry time.");
  });

  it("ignores a malformed change and keeps only inline images", () => {
    expect(parseReview("not json")).toBeUndefined();
    expect(parseReview(JSON.stringify({ verified: true }))).toBeUndefined();
    const review = parseReview(JSON.stringify({ ...fixture, images: { "a.png": "data:image/png;base64,AA", "b.png": "https://example.com/b.png" } }));
    expect(Object.keys(review?.images ?? {})).toEqual(["a.png"]);
  });

  it("opens on the change: its proofs, the pull request and the tabs, with comments but no vote", async () => {
    const review = parseReview(REVIEW);
    const page = await html(
      <SharedView state={{ status: "ready", kind: "v2", title: "Rate-limit the export API", docs: DOCS, review }} onComment={noComment} />,
    );
    expect(page).toContain("The change");
    expect(page).toContain("A 61st export in an hour is refused with a retry time.");
    expect(page).toContain("Proven");
    expect(page).toContain("#42");
    for (const tab of [">Overview<", ">Evidence<", ">Try it<"]) expect(page).toContain(tab);
    expect(page).toContain("Add comment");
    expect(page).not.toContain("Request changes");
    expect(page).not.toContain(">Approve<");
    expect(page).not.toContain("Files changed");
  });

  it("anchors a check the way the Cockpit does", () => {
    expect(checkId("scenario 1")).toBe("scenario:1");
    expect(checkId("dod T3")).toBe("dod:T3");
  });

  it("sends a new thread as the Cockpit reads it, with no verdict", () => {
    const payload = changePayload(
      { author: " Sam ", remark: " Is 429 right? ", thread: "g-abc123", anchor: { kind: "doneMeans", id: "1", quote: "A 61st export" } },
      7,
    );
    expect(payload).toMatchObject({ author: "Sam", createdAt: 7, annotations: [{ blockId: "review", text: "Is 429 right?" }] });
    expect(payload.decision).toBeUndefined();
    expect(JSON.parse(payload.annotations[0].originalText)).toEqual({
      t: "thread",
      thread: "g-abc123",
      anchor: { kind: "doneMeans", id: "1", quote: "A 61st export" },
    });
  });

  it("sends a reply to the guest's own thread, to the same feedback endpoint", async () => {
    const fetchFn = answer(201, { ok: true });
    expect(await submitChangeComment(V2_ID, KEY, { author: "Sam", remark: "Thanks", replyTo: "g-abc123" }, fetchFn)).toEqual({ ok: true });
    const sent = await sentPayload(fetchFn);
    expect(sent.id).toBe(V2_ID);
    const opened = JSON.parse((await openFromLink(KEY, "feedback", sent.payload)) ?? "null") as { annotations: { originalText: string }[] };
    expect(JSON.parse(opened.annotations[0].originalText)).toEqual({ t: "reply", thread: "g-abc123" });
  });
});

/** What a submission put on the wire: the link's id and the sealed payload, with the URL it went to checked. */
async function sentPayload(fetchFn: typeof fetch): Promise<{ id: string; payload: { v: 3; iv: string; ct: string } }> {
  const [url, init] = (fetchFn as unknown as { mock: { calls: [string, RequestInit][] } }).mock.calls[0] as [string, RequestInit];
  expect(url).toBe("/api/share/feedback");
  return JSON.parse(String(init.body));
}

describe("commenting", () => {
  it("leaves as v11's annotation, sealed with the link's key: the document is the block, the passage the original text", async () => {
    const fetchFn = answer(201, { ok: true, position: 0 });
    const result = await submitComment(
      V2_ID,
      KEY,
      { author: "  Guest Gina ", doc: "02-design.md", quote: "One Vercel deployment", remark: "Why one?" },
      fetchFn,
    );
    expect(result).toEqual({ ok: true });
    const sent = await sentPayload(fetchFn);
    expect(sent.id).toBe(V2_ID);
    // The server sees an envelope and nothing of the words.
    expect(Object.keys(sent.payload).sort()).toEqual(["ct", "iv", "v"]);
    expect(JSON.stringify(sent)).not.toContain("Why one?");
    expect(JSON.parse((await openFromLink(KEY, "feedback", sent.payload)) ?? "null")).toMatchObject({
      author: "Guest Gina",
      annotations: [{ blockId: "02-design.md", originalText: "One Vercel deployment", text: "Why one?" }],
    });
  });

  it("sends a verdict alone, without an annotation, as v11's decision", () => {
    expect(feedbackPayload({ author: "", doc: "README.md", quote: "", remark: "", verdict: "approve" }, 5)).toEqual({
      author: "Guest",
      createdAt: 5,
      annotations: [],
      decision: { verdict: "approve" },
    });
  });

  it("refuses a comment the owner's machine would drop, instead of sending it into silence", async () => {
    const never = answer(201, { ok: true });
    const long = { author: "G", doc: "README.md", quote: "", remark: "x".repeat(4001) };
    expect(await submitComment(V2_ID, KEY, long, never)).toEqual({ ok: false, reason: "too_large" });
    expect(await submitComment(V2_ID, KEY, { ...long, remark: "ok", author: "G".repeat(81) }, never)).toEqual({ ok: false, reason: "too_large" });
    expect(never).not.toHaveBeenCalled();
  });

  it("tells a revoked link, a busy connection and a long comment apart", async () => {
    const input = { author: "G", doc: "README.md", quote: "", remark: "x" };
    expect(await submitComment(V2_ID, KEY, input, answer(404))).toEqual({ ok: false, reason: "gone" });
    expect(await submitComment(V2_ID, KEY, input, answer(429))).toEqual({ ok: false, reason: "rate_limited" });
    expect(await submitComment(V2_ID, KEY, input, answer(413))).toEqual({ ok: false, reason: "too_large" });
    expect(await submitComment(V2_ID, KEY, input, answer(500))).toEqual({ ok: false, reason: "network" });
  });
});
