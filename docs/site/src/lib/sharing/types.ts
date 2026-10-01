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
 * GitHub-PR-style top-level review verdict. Submitted from the shared-plan page
 * alongside (or independently of) inline annotations on the same feedback batch.
 */
export interface Decision {
  verdict: "approve" | "request_changes";
  /** Free-text comment, 0–4000 chars (server-enforced). */
  comment?: string;
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
  /** Optional top-level review verdict for this submit. */
  decision?: Decision;
}

// ─── Multi-user feedback polling (2026-05-15) ─────────────────────────────────
// QualityLayer's Cockpit polls this feedback queue API; preserve its request and response shapes.

/** One submission on the server-side feedback queue for a single share id. */
export interface FeedbackQueueEntry {
  /** Server-assigned 0-based position in the share's feedback list (= RPUSH return - 1). */
  position: number;
  /** When the server received this submission (server-side Date.now()). */
  receivedAt: number;
  /** The submitted feedback batch. */
  payload: FeedbackPayload;
}

/** Client → feedback API batch-read request body. */
export interface FeedbackBatchRequest {
  items: Array<{ id: string; cursor: number }>;
}

/** Feedback API → client batch-read response. Keyed by share id. */
export type FeedbackBatchResponse = Record<
  string,
  {
    entries: FeedbackQueueEntry[];
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
>;
