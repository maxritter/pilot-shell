/**
 * The annotation and feedback contracts of shared plans. Task documents and link
 * loading are defined in sharing.ts. Keep these wire shapes stable.
 */

export interface Annotation {
  id: string;
  blockId: string;
  /** The text that was selected */
  originalText: string;
  /** User's free-text annotation */
  text: string;
  createdAt: number;
  /** Attribution — set for feedback annotations from collaborators */
  author?: string;
  /**
   * @deprecated Legacy accept/reject lifecycle (pre-2026-05-15). New code
   * never sets this field; legacy values are stripped on load. Kept on the
   * interface only so older `.annotations` JSON parses without error.
   */
  feedbackStatus?: "pending" | "accepted" | "rejected";
  /** When this annotation was imported from teammate feedback */
  importedAt?: number;
}

/**
 * Sealed text, as a link's plan and a guest's submission travel: AES-GCM under the link's key
 * (`iv` 12 bytes and `ct`, both base64). The server holds it without the key.
 */
export interface SealedPayload {
  v: 3;
  iv: string;
  ct: string;
}

/** Payload for sending feedback annotations back (B→A direction) */
export interface FeedbackPayload {
  /** Annotations created by the recipient */
  annotations: Annotation[];
  /** Display name of the feedback author */
  author: string;
  /** Plan path from the original share (for matching on import) */
  planPath?: string;
  /** Timestamp when feedback was created */
  createdAt: number;
}

// ─── Multi-user feedback polling (2026-05-15) ─────────────────────────────────
// QualityLayer's App polls this feedback queue API; preserve its request and response shapes.

/** One submission on the server-side feedback queue for a single share id. */
export interface FeedbackQueueEntry {
  /** Server-assigned 0-based position in the share's feedback list (= RPUSH return - 1). */
  position: number;
  /** When the server received this submission (server-side Date.now()). */
  receivedAt: number;
  /** The submitted feedback batch: sealed with the link's key, or a plain one an older page sent. */
  payload: SealedPayload | FeedbackPayload;
}

/** Client → feedback API batch-read request body. */
export interface FeedbackBatchRequest {
  /**
   * `since` is the change number the client last read for that link (`rev` of an earlier answer);
   * a link still at that number answers `{ unchanged: true }` and costs no database read.
   */
  items: Array<{ id: string; cursor: number; since?: number }>;
}

/** What the batch answers for a link that has not changed since the number the client sent. */
export interface FeedbackBatchUnchanged {
  unchanged: true;
}

/** Feedback API → client batch-read response. Keyed by share id. */
export type FeedbackBatchResponse = Record<string, FeedbackBatchRead | FeedbackBatchUnchanged>;

/** What the batch answers for a link it read. */
export interface FeedbackBatchRead {
  entries: FeedbackQueueEntry[];
  /** The link's change number as it stood before this read: send it back as `since` on the next poll. Absent for a link that is not found. */
  rev?: number;
  /** Cursor to send on the next poll. Equals the input cursor when entries is empty. */
  cursor: number;
  /** Present only when `share:<id>` does not exist (expired or never created). */
  error?: "not_found";
  /**
   * Set true when the server returned a full page of entries; the client
   * should re-poll immediately rather than wait for the next 60s tick.
   * Absent or false means the queue was fully drained by this read.
   */
  hasMore?: boolean;
}
