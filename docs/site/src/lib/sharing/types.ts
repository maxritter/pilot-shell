/**
 * Types for the secure spec sharing system.
 * Ported from console/src/shared/sharing/types.ts — kept in sync.
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
  /** Feedback lifecycle for imported external annotations */
  feedbackStatus?: "pending" | "accepted" | "rejected";
  /** When this annotation was imported */
  importedAt?: number;
}

/** Payload for sharing a spec with another user (A→B direction) */
export interface SharePayload {
  /** Full markdown content of the spec */
  specContent: string;
  /** Existing annotations from the spec owner */
  annotations: Annotation[];
  /** Display name of the sharer */
  author?: string;
  /** Original plan file path */
  planPath?: string;
  /** Whether this is a specification or requirement */
  contentType?: "specification" | "requirement";
  /** Timestamp when the share was created */
  createdAt: number;
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
