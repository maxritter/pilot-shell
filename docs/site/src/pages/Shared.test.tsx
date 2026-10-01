import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it, vi } from "vitest";
import fixture from "@/lib/sharing/shared-review.fixture.json";
import {
  changePayload,
  checkId,
  feedbackPayload,
  loadShare,
  parseReview,
  submitChangeComment,
  submitComment,
} from "@/lib/sharing/sharing";
import { SharedView } from "./Shared";

/**
 * The page a link opens: a v2 plan with its documents, and "no longer shared" for a link
 * that is gone. Comments leave in v11's annotation format, which v2 links still use.
 */

const V2_ID = "A".repeat(22);
const DOCS = { "README.md": "# Task\n\nThe problem.", "02-design.md": "# Design\n\nOne Vercel deployment." };

const answer = (status: number, body?: unknown) =>
  vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })) as unknown as typeof fetch;

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

describe("loading a link", () => {
  it("reads a v2 plan with its documents and expiry", async () => {
    const fetchFn = answer(200, { v: 2, task: "Pager off-by-one", docs: DOCS, expires: "2026-10-14T10:00:00.000Z" });
    const loaded = await loadShare(V2_ID, fetchFn);
    expect(loaded).toEqual({ status: "ready", kind: "v2", title: "Pager off-by-one", docs: DOCS, expires: "2026-10-14T10:00:00.000Z" });
    expect(fetchFn).toHaveBeenCalledWith(`/api/share?id=${V2_ID}`);
  });

  it("says a revoked or expired link is gone, and a damaged or unreachable one is an error", async () => {
    expect(await loadShare(V2_ID, answer(404, { error: "Share not found or expired" }))).toEqual({ status: "gone" });
    expect(await loadShare(V2_ID, answer(500))).toMatchObject({ status: "error" });
    expect(await loadShare(V2_ID, answer(200, { data: "not-a-payload" }))).toMatchObject({ status: "error" });
    const offline = vi.fn(async () => {
      throw new Error("offline");
    }) as unknown as typeof fetch;
    expect(await loadShare(V2_ID, offline)).toMatchObject({ status: "error" });
    // An id of the wrong shape never reaches the network.
    const never = answer(200, {});
    expect(await loadShare("short", never)).toMatchObject({ status: "error" });
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
    const loaded = await loadShare(V2_ID, answer(200, { v: 2, task: "Rate-limit the export API", docs: { ...DOCS, "review.json": REVIEW } }));
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
    expect(await submitChangeComment(V2_ID, { author: "Sam", remark: "Thanks", replyTo: "g-abc123" }, fetchFn)).toEqual({ ok: true });
    const [url, init] = (fetchFn as unknown as { mock: { calls: [string, RequestInit][] } }).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/share/feedback");
    const sent = JSON.parse(String(init.body)) as { payload: { annotations: { originalText: string }[] } };
    expect(JSON.parse(sent.payload.annotations[0].originalText)).toEqual({ t: "reply", thread: "g-abc123" });
  });
});

describe("commenting", () => {
  it("leaves as v11's annotation: the document is the block, the passage the original text", async () => {
    const fetchFn = answer(201, { ok: true, position: 0 });
    const result = await submitComment(
      V2_ID,
      { author: "  Guest Gina ", doc: "02-design.md", quote: "One Vercel deployment", remark: "Why one?" },
      fetchFn,
    );
    expect(result).toEqual({ ok: true });
    const [url, init] = (fetchFn as unknown as { mock: { calls: [string, RequestInit][] } }).mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/share/feedback");
    expect(JSON.parse(String(init.body))).toMatchObject({
      id: V2_ID,
      payload: {
        author: "Guest Gina",
        annotations: [{ blockId: "02-design.md", originalText: "One Vercel deployment", text: "Why one?" }],
      },
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

  it("tells a revoked link, a busy connection and a long comment apart", async () => {
    const input = { author: "G", doc: "README.md", quote: "", remark: "x" };
    expect(await submitComment(V2_ID, input, answer(404))).toEqual({ ok: false, reason: "gone" });
    expect(await submitComment(V2_ID, input, answer(429))).toEqual({ ok: false, reason: "rate_limited" });
    expect(await submitComment(V2_ID, input, answer(413))).toEqual({ ok: false, reason: "too_large" });
    expect(await submitComment(V2_ID, input, answer(500))).toEqual({ ok: false, reason: "network" });
  });
});
