/**
 * High-level URL generation and parsing for secure spec sharing.
 *
 * Website URL format: https://pilot-shell.com/shared#<ciphertext>?key=<aesKey>
 * Console URL formats (for paste-input parsing):
 *   - https://localhost:PORT/#/shared/<data>?key=<key>
 *   - https://localhost:PORT/#/feedback/<data>?key=<key>
 *
 * All data lives in the hash fragment, which the HTTP spec guarantees
 * is never sent to the server.
 */

import { compress, decompress } from "./compress";
import { encrypt, decrypt } from "./crypto";
import type { SharePayload, FeedbackPayload } from "./types";

/** ~32KB limit — safe for all major browsers */
const MAX_INLINE_BYTES = 32_768;

export interface WebShareUrlResult {
  url: string;
  key: string;
}

/** Compress, encrypt, and build a URL. Returns null if too large or on error. */
async function buildEncryptedUrl(
  payload: unknown,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  try {
    const compressed = await compress(JSON.stringify(payload));
    const { ciphertext, key } = await encrypt(compressed);

    if (ciphertext.length > MAX_INLINE_BYTES) {
      return null;
    }

    const url = `${baseUrl}#${ciphertext}?key=${key}`;
    return { url, key };
  } catch {
    return null;
  }
}

/** Generate a web share URL. Returns null if payload would exceed inline URL limits. */
export function generateWebShareUrl(
  payload: SharePayload,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  return buildEncryptedUrl(payload, baseUrl);
}

/** Generate a web feedback URL. Returns null if payload would exceed inline URL limits. */
export function generateWebFeedbackUrl(
  payload: FeedbackPayload,
  baseUrl: string,
): Promise<WebShareUrlResult | null> {
  return buildEncryptedUrl(payload, baseUrl);
}

/**
 * Parse hash fragment + key from any supported URL format:
 *   - Website: pilot-shell.com/shared#<data>?key=<key>
 *   - Console shared: localhost/#/shared/<data>?key=<key>
 *   - Console feedback: localhost/#/feedback/<data>?key=<key>
 *   - Raw hash: #<data>?key=<key>
 *
 * Returns null if no data could be extracted.
 */
export function parseHashFragment(input: string): { data: string; key: string } | null {
  const hashIdx = input.indexOf("#");
  if (hashIdx === -1) return null;

  const fragment = input.slice(hashIdx + 1);
  const qIdx = fragment.indexOf("?");
  const path = qIdx === -1 ? fragment : fragment.slice(0, qIdx);
  const queryStr = qIdx === -1 ? "" : fragment.slice(qIdx + 1);
  const key = new URLSearchParams(queryStr).get("key") ?? "";

  // Strip known Console path prefixes
  let data = path;
  if (data.startsWith("/shared/")) data = data.slice("/shared/".length);
  else if (data.startsWith("/feedback/")) data = data.slice("/feedback/".length);

  if (!data || !key) return null;
  return { data, key };
}

/**
 * Decrypt and decompress a share payload.
 * Returns null on any failure.
 */
export async function decryptSharePayload(
  data: string,
  key: string,
): Promise<SharePayload | null> {
  try {
    const compressed = await decrypt(data, key);
    return JSON.parse(await decompress(compressed)) as SharePayload;
  } catch {
    return null;
  }
}

/**
 * Decrypt and decompress a feedback payload.
 * Returns null on any failure.
 */
export async function decryptFeedbackPayload(
  data: string,
  key: string,
): Promise<FeedbackPayload | null> {
  try {
    const compressed = await decrypt(data, key);
    return JSON.parse(await decompress(compressed)) as FeedbackPayload;
  } catch {
    return null;
  }
}

/**
 * Detect whether a decrypted payload is a SharePayload (has specContent)
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
 * Decrypt any payload from a hash fragment, auto-detecting type.
 */
export async function decryptHashPayload(
  data: string,
  key: string,
): Promise<{ type: "share"; payload: SharePayload } | { type: "feedback"; payload: FeedbackPayload } | null> {
  try {
    const compressed = await decrypt(data, key);
    const parsed = JSON.parse(await decompress(compressed));
    if (isSharePayload(parsed)) {
      return { type: "share", payload: parsed as SharePayload };
    }
    return { type: "feedback", payload: parsed as FeedbackPayload };
  } catch {
    return null;
  }
}
