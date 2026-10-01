/**
 * The shared-plan page's client: read a link and send a comment.
 *
 *   https://qualitylayer.dev/s/<22 characters>   documents as plain text, 14 days
 *
 * Comments go to POST /api/share/feedback in an annotation format, so the owner's
 * Cockpit reads them. Anyone with the link may read and comment; the link itself
 * is the access token.
 */

import type { Decision, FeedbackPayload } from "./types";

export const SHARE_ID = /^[A-Za-z0-9]{22}$/;

export type LoadedShare =
  | {
      status: "ready";
      kind: "v2";
      title: string;
      /** Documents by name, in the order to show them. */
      docs: Record<string, string>;
      /** ISO time the link runs out. */
      expires?: string;
      /** The finished, verified change, when the task got that far (v2 only). */
      review?: SharedReview;
    }
  /** Revoked, expired, or never there. */
  | { status: "gone" }
  | { status: "error"; message: string };

/**
 * What a link reviewer reads of the finished change: the Cockpit's SharedReview
 * (qualitylayer/src/core/review/detail.ts), sent as `docs["review.json"]` once a
 * fresh check has passed. It holds the proofs and evidence only, never threads,
 * reviewers, source, the diff or logs. Only the fields this page shows are typed.
 */
export type SharedReview = {
  round: number | null;
  judge: string | null;
  verified: boolean;
  doneMeans: { n: number; head: string; text: string; proven: boolean; proof: string; evidence: string[] }[];
  tiles: {
    key: string;
    label: string;
    passed: number;
    total: number;
    lines: { ok: boolean; label: string; text: string; evidence: string[] }[];
  }[];
  pictures: { file: string; caption: string }[];
  proofs: { file: string; title: string; caption: string }[];
  second: { name: string; state: string; findings: number | null } | null;
  tryIt: { text: string; command: string | null }[];
  notVerified: string[];
  pr: { number: number | null; title: string; url: string; state: string; checks: string; branch: string } | null;
  images: Record<string, string>;
};

/** The change's document in a v2 share; it is data, not a document to read. */
export const REVIEW_DOC = "review.json";

const isList = (v: unknown): v is unknown[] => Array.isArray(v);

/** The shared change from untrusted JSON, or undefined when it is missing or malformed. */
export function parseReview(text: string | undefined): SharedReview | undefined {
  if (text === undefined) return undefined;
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    return undefined;
  }
  if (typeof value !== "object" || value === null) return undefined;
  const r = value as Partial<SharedReview>;
  if (typeof r.verified !== "boolean" || !isList(r.doneMeans) || !isList(r.tiles)) return undefined;
  return {
    round: typeof r.round === "number" ? r.round : null,
    judge: typeof r.judge === "string" ? r.judge : null,
    verified: r.verified,
    doneMeans: r.doneMeans,
    tiles: r.tiles,
    pictures: isList(r.pictures) ? r.pictures : [],
    proofs: isList(r.proofs) ? r.proofs : [],
    second: r.second ?? null,
    tryIt: isList(r.tryIt) ? r.tryIt : [],
    notVerified: isList(r.notVerified) ? r.notVerified : [],
    pr: r.pr ?? null,
    // Only inline images: a picture never makes the page fetch from elsewhere.
    images: Object.fromEntries(
      Object.entries(r.images ?? {}).filter(([, url]) => typeof url === "string" && url.startsWith("data:image/")),
    ),
  };
}

/** The documents a person reads, in the order the work produced them. */
const ORDER = ["README.md", "01-research.md", "01-diagnosis.md", "02-design.md", "03-outline-overview.md"];

export function orderedDocs(docs: Record<string, string>): string[] {
  const known = ORDER.filter((name) => docs[name] !== undefined);
  return [
    ...known,
    ...Object.keys(docs).filter((name) => !known.includes(name) && !name.startsWith("artifacts/") && name !== REVIEW_DOC),
  ];
}

/** Read a share link's plan: its documents as they are. */
export async function loadShare(id: string, fetchFn: typeof fetch = fetch): Promise<LoadedShare> {
  if (!SHARE_ID.test(id)) return { status: "error", message: "This does not look like a share link." };
  let res: Response;
  try {
    res = await fetchFn(`/api/share?id=${encodeURIComponent(id)}`);
  } catch {
    return { status: "error", message: "The share service could not be reached. Try again in a moment." };
  }
  if (res.status === 404) return { status: "gone" };
  if (!res.ok) return { status: "error", message: "The plan could not be loaded. Try again in a moment." };

  const body = (await res.json().catch(() => null)) as {
    v?: number;
    task?: string;
    docs?: Record<string, string>;
    expires?: string;
  } | null;
  if (body?.v === 2 && body.docs !== undefined) {
    const review = parseReview(body.docs[REVIEW_DOC]);
    const { [REVIEW_DOC]: _review, ...docs } = body.docs;
    return {
      status: "ready",
      kind: "v2",
      title: body.task ?? "Shared plan",
      docs,
      expires: body.expires,
      ...(review !== undefined ? { review } : {}),
    };
  }
  return { status: "error", message: "The plan could not be loaded." };
}

export type SubmitResult = { ok: true } | { ok: false; reason: "gone" | "rate_limited" | "too_large" | "network" };

export type CommentInput = {
  /** Who is commenting, typed by them. */
  author: string;
  /** The document the passage is in. */
  doc: string;
  /** The passage selected; empty for a general remark. */
  quote: string;
  remark: string;
  /** A verdict on the plan, with or without a remark. */
  verdict?: Decision["verdict"];
};

/** The comment in the annotation format: the block is the document, the original text the passage. */
export function feedbackPayload(input: CommentInput, now = Date.now()): FeedbackPayload {
  const remark = input.remark.trim();
  return {
    author: input.author.trim() || "Guest",
    createdAt: now,
    annotations:
      remark === ""
        ? []
        : [
            {
              id: crypto.randomUUID(),
              blockId: input.doc,
              originalText: input.quote,
              text: remark,
              createdAt: now,
            },
          ],
    ...(input.verdict !== undefined ? { decision: { verdict: input.verdict } } : {}),
  };
}

/** A place in the shared change a comment is about, as the Cockpit anchors it. */
export type ChangeAnchor = { kind: "doneMeans" | "picture" | "check"; id: string; quote?: string };

/** A link reviewer's comment on the change: a new thread on an anchor, or a reply to their own thread. */
export type ChangeCommentInput = { author: string; remark: string } & (
  | { anchor: ChangeAnchor; thread: string }
  | { replyTo: string }
);

/** A check line's anchor id, as the Cockpit forms it: "scenario 1" → "scenario:1". */
export const checkId = (label: string) => label.replace(" ", ":");

/** A new thread id, in the form the Cockpit gives guest threads. */
export const newThreadId = () => `g-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`;

/**
 * A comment on the change in the annotation format: the block is the review,
 * the original text a small JSON head the Cockpit decodes (core/review/threads.ts
 * fromWire). A link reviewer never sends a verdict.
 */
export function changePayload(input: ChangeCommentInput, now = Date.now()): FeedbackPayload {
  const head =
    "replyTo" in input
      ? { t: "reply", thread: input.replyTo }
      : {
          t: "thread",
          thread: input.thread,
          anchor: { ...input.anchor, ...(input.anchor.quote ? { quote: input.anchor.quote.slice(0, 300) } : {}) },
        };
  return {
    author: input.author.trim() || "Guest",
    createdAt: now,
    annotations: [{ id: crypto.randomUUID(), blockId: "review", originalText: JSON.stringify(head), text: input.remark.trim(), createdAt: now }],
  };
}

/** Send a comment on the shared change to its owner. */
export function submitChangeComment(id: string, input: ChangeCommentInput, fetchFn: typeof fetch = fetch): Promise<SubmitResult> {
  return post(id, changePayload(input), fetchFn);
}

/** Send a comment to the plan's owner. */
export function submitComment(id: string, input: CommentInput, fetchFn: typeof fetch = fetch): Promise<SubmitResult> {
  return post(id, feedbackPayload(input), fetchFn);
}

async function post(id: string, payload: FeedbackPayload, fetchFn: typeof fetch): Promise<SubmitResult> {
  let res: Response;
  try {
    res = await fetchFn("/api/share/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, payload }),
    });
  } catch {
    return { ok: false, reason: "network" };
  }
  if (res.ok) return { ok: true };
  if (res.status === 404) return { ok: false, reason: "gone" };
  if (res.status === 413) return { ok: false, reason: "too_large" };
  if (res.status === 429) return { ok: false, reason: "rate_limited" };
  return { ok: false, reason: "network" };
}
