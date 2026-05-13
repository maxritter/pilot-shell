/**
 * High-level URL generation and parsing for spec sharing.
 *
 * Two URL families coexist:
 *
 *   1. Short URL (current): https://pilot-shell.com/s/<8-char-id>
 *      Payload POSTed to /api/share and stored on Upstash Redis for ≤ 3 days;
 *      anyone with the link can fetch and view. See `generateShortFeedbackUrl`.
 *
 *   2. Legacy fragment URL (back-compat only): https://pilot-shell.com/shared#<compressed-data>
 *      Compressed payload embedded in the URL fragment; never transmitted to the server.
 *      Still decoded by `Shared.tsx` so in-flight legacy links keep working.
 *
 * No encryption — both formats rely on the unguessable URL itself as the access token.
 */

import { compress, decompress } from "./compress";
import type { SharePayload, FeedbackPayload } from "./types";

/** ~32KB limit — safe for all major browsers */
const MAX_INLINE_BYTES = 32_768;

export interface WebShareUrlResult {
  url: string;
}

/** Compress and build a URL. Returns null if too large or on error. */
async function buildCompressedUrl(
  payload: unknown,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  try {
    const compressed = await compress(JSON.stringify(payload));

    if (compressed.length > MAX_INLINE_BYTES) {
      return null;
    }

    const url = `${baseUrl}#${compressed}`;
    return { url };
  } catch {
    return null;
  }
}

/** Generate a web share URL. Returns null if payload would exceed inline URL limits. */
export function generateWebShareUrl(
  payload: SharePayload,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  return buildCompressedUrl(payload, baseUrl);
}

/** Generate a web feedback URL. Returns null if payload would exceed inline URL limits. */
export function generateWebFeedbackUrl(
  payload: FeedbackPayload,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  return buildCompressedUrl(payload, baseUrl);
}

export type ShortShareResult =
  | { ok: true; url: string }
  | { ok: false; reason: "too_large" | "rate_limited" | "network" | "timeout" };

const SHARE_POST_TIMEOUT_MS = 10_000;

/**
 * Compress + upload the feedback payload to /api/share and return the short URL.
 * Used by the recipient on pilot-shell.com to send annotations back to the sharer.
 */
export async function generateShortFeedbackUrl(
  payload: FeedbackPayload,
  apiBaseUrl: string = "",
): Promise<ShortShareResult> {
  let compressed: string;
  try {
    compressed = await compress(JSON.stringify(payload));
  } catch {
    return { ok: false, reason: "network" };
  }
  let res: Response;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), SHARE_POST_TIMEOUT_MS);
  try {
    res = await fetch(`${apiBaseUrl}/api/share`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: compressed }),
      signal: controller.signal,
    });
  } catch (err) {
    if (controller.signal.aborted) return { ok: false, reason: "timeout" };
    if (err instanceof DOMException && err.name === "AbortError") return { ok: false, reason: "timeout" };
    return { ok: false, reason: "network" };
  } finally {
    clearTimeout(timeoutId);
  }
  if (res.status === 413) return { ok: false, reason: "too_large" };
  if (res.status === 429) return { ok: false, reason: "rate_limited" };
  if (!res.ok) return { ok: false, reason: "network" };
  try {
    const { id } = (await res.json()) as { id: string };
    if (!id || !/^[A-Za-z0-9]{8}$/.test(id)) {
      return { ok: false, reason: "network" };
    }
    return { ok: true, url: `https://pilot-shell.com/s/${id}` };
  } catch {
    return { ok: false, reason: "network" };
  }
}

/**
 * Parse hash fragment from any supported URL format:
 *   - Website: pilot-shell.com/shared#<data>
 *   - Console shared: localhost/#/shared/<data>
 *   - Console feedback: localhost/#/feedback/<data>
 *   - Raw hash: #<data>
 *
 * Returns null if no data could be extracted.
 */
export function parseHashFragment(input: string): { data: string } | null {
  const hashIdx = input.indexOf("#");
  if (hashIdx === -1) return null;

  const fragment = input.slice(hashIdx + 1);
  // Strip any legacy ?key= params
  const qIdx = fragment.indexOf("?");
  const path = qIdx === -1 ? fragment : fragment.slice(0, qIdx);

  // Strip known Console path prefixes
  let data = path;
  if (data.startsWith("/shared/")) data = data.slice("/shared/".length);
  else if (data.startsWith("/feedback/")) data = data.slice("/feedback/".length);

  if (!data) return null;
  return { data };
}

/**
 * Decompress a share payload.
 * Returns null on any failure.
 */
export async function decompressSharePayload(
  data: string,
): Promise<SharePayload | null> {
  if (!data) return null;
  try {
    return JSON.parse(await decompress(data)) as SharePayload;
  } catch {
    return null;
  }
}

/**
 * Decompress a feedback payload.
 * Returns null on any failure.
 */
export async function decompressFeedbackPayload(
  data: string,
): Promise<FeedbackPayload | null> {
  if (!data) return null;
  try {
    return JSON.parse(await decompress(data)) as FeedbackPayload;
  } catch {
    return null;
  }
}

/**
 * Detect whether a payload is a SharePayload (has specContent)
 * vs a FeedbackPayload (has only annotations + author).
 */
export function isSharePayload(payload: unknown): payload is SharePayload {
  return (
    typeof payload === "object" &&
    payload !== null &&
    "specContent" in payload &&
    typeof (payload as SharePayload).specContent === "string"
  );
}

/**
 * Decompress any payload from a hash fragment, auto-detecting type.
 */
export async function decompressHashPayload(
  data: string,
): Promise<{ type: "share"; payload: SharePayload } | { type: "feedback"; payload: FeedbackPayload } | null> {
  if (!data) return null;
  try {
    const parsed = JSON.parse(await decompress(data));
    if (isSharePayload(parsed)) {
      return { type: "share", payload: parsed as SharePayload };
    }
    return { type: "feedback", payload: parsed as FeedbackPayload };
  } catch {
    return null;
  }
}
