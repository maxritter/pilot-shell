/**
 * The shared-plan page's client: read a link and send a comment.
 *
 *   https://qualitylayer.dev/s/<22 characters>#<43 characters>   sealed plan, 14 days
 *
 * The plan and every comment are sealed in the browser with a key that only the link's
 * fragment carries, so the server holds ciphertext and never receives the key (a fragment
 * is not sent). Comments go to POST /api/share/feedback in an annotation format, so the
 * owner's Cockpit reads them. Anyone with the whole link may read and comment.
 */

import type { Decision, FeedbackPayload, SealedPayload } from "./types";

export const SHARE_ID = /^[A-Za-z0-9]{22}$/;

/** 32 random bytes, base64url without padding. */
const LINK_KEY = /^[A-Za-z0-9_-]{43}$/;

/** The key a link's fragment carries, or "" when the link has none (or not a whole one). */
export function linkKeyOf(hash: string): string {
  const key = hash.startsWith("#") ? hash.slice(1) : hash;
  return LINK_KEY.test(key) ? key : "";
}

/** What a seal is for: the key is the link's, the purpose keeps a comment from passing as a plan. */
type Purpose = "plan" | "feedback";

const utf8 = (text: string) => new TextEncoder().encode(text);

function toBase64(bytes: Uint8Array): string {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

const fromBase64 = (text: string) => Uint8Array.from(atob(text), (c) => c.charCodeAt(0));

const aesKey = (key: string, usage: KeyUsage) =>
  crypto.subtle.importKey("raw", fromBase64(key.replace(/-/g, "+").replace(/_/g, "/") + "=") as BufferSource, "AES-GCM", false, [usage]);

const additionalData = (purpose: Purpose) => utf8(`ql-link|${purpose}`) as BufferSource;

/** Seal `plain` with the link's key (AES-GCM, a fresh 12-byte iv, both base64). */
export async function sealForLink(key: string, purpose: Purpose, plain: string): Promise<SealedPayload> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv as BufferSource, additionalData: additionalData(purpose) },
    await aesKey(key, "encrypt"),
    utf8(plain) as BufferSource,
  );
  return { v: 3, iv: toBase64(iv), ct: toBase64(new Uint8Array(ct)) };
}

/** What a seal holds, or null when it is not one, was sealed for another purpose or with another key. */
export async function openFromLink(key: string, purpose: Purpose, sealed: unknown): Promise<string | null> {
  const s = sealed as Partial<SealedPayload> | null;
  if (typeof s !== "object" || s === null || s.v !== 3 || typeof s.iv !== "string" || typeof s.ct !== "string") return null;
  try {
    const plain = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: fromBase64(s.iv) as BufferSource, additionalData: additionalData(purpose) },
      await aesKey(key, "decrypt"),
      fromBase64(s.ct) as BufferSource,
    );
    return new TextDecoder().decode(plain);
  } catch {
    return null;
  }
}

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
  /** The link was copied without the part after `#`: nothing to open the plan with. */
  | { status: "no-key" }
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

/** The plan a link holds: its title and the documents, as text. What opened is still untrusted, so it is rebuilt. */
function parsePlan(text: string | null): { task: string; docs: Record<string, string> } | null {
  if (text === null) return null;
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    return null;
  }
  const plan = value as { task?: unknown; docs?: unknown } | null;
  if (typeof plan !== "object" || plan === null || typeof plan.docs !== "object" || plan.docs === null) return null;
  const docs = Object.fromEntries(
    Object.entries(plan.docs).filter((entry): entry is [string, string] => typeof entry[1] === "string"),
  );
  return { task: typeof plan.task === "string" ? plan.task : "Shared plan", docs };
}

/** Read a share link's plan: fetch the sealed copy and open it with the link's key. */
export async function loadShare(id: string, key: string, fetchFn: typeof fetch = fetch): Promise<LoadedShare> {
  if (!SHARE_ID.test(id)) return { status: "error", message: "This does not look like a share link." };
  if (key === "") return { status: "no-key" };
  let res: Response;
  try {
    res = await fetchFn(`/api/share?id=${encodeURIComponent(id)}`);
  } catch {
    return { status: "error", message: "The share service could not be reached. Try again in a moment." };
  }
  if (res.status === 404) return { status: "gone" };
  if (!res.ok) return { status: "error", message: "The plan could not be loaded. Try again in a moment." };

  const body = (await res.json().catch(() => null)) as { expires?: string } | null;
  const plan = parsePlan(await openFromLink(key, "plan", body));
  if (plan === null)
    return { status: "error", message: "The plan could not be opened. Check that the whole link was copied." };
  const review = parseReview(plan.docs[REVIEW_DOC]);
  const { [REVIEW_DOC]: _review, ...docs } = plan.docs;
  return {
    status: "ready",
    kind: "v2",
    title: plan.task,
    docs,
    expires: body?.expires,
    ...(review !== undefined ? { review } : {}),
  };
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
export function submitChangeComment(id: string, key: string, input: ChangeCommentInput, fetchFn: typeof fetch = fetch): Promise<SubmitResult> {
  return post(id, key, changePayload(input), fetchFn);
}

/** Send a comment to the plan's owner. */
export function submitComment(id: string, key: string, input: CommentInput, fetchFn: typeof fetch = fetch): Promise<SubmitResult> {
  return post(id, key, feedbackPayload(input), fetchFn);
}

/** What the owner's machine keeps of a comment: it drops a longer one, and the server cannot say so any more (it holds ciphertext). */
const MAX_AUTHOR = 80;
const MAX_TEXT = 4_000;
const fits = (p: FeedbackPayload) =>
  p.author.length <= MAX_AUTHOR && p.annotations.every((a) => a.text.length <= MAX_TEXT && a.originalText.length <= MAX_TEXT);

async function post(id: string, key: string, payload: FeedbackPayload, fetchFn: typeof fetch): Promise<SubmitResult> {
  if (!fits(payload)) return { ok: false, reason: "too_large" };
  let res: Response;
  try {
    res = await fetchFn("/api/share/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, payload: await sealForLink(key, "feedback", JSON.stringify(payload)) }),
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
