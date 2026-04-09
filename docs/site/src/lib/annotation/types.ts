/**
 * Standalone annotation types for the website.
 * Ported from console/src/ui/viewer/views/Spec/annotation/types.ts
 * without Console-specific dependencies (CodeAnnotation, UnifiedAnnotationStore).
 */

export interface Annotation {
  id: string;
  blockId: string;
  /** The text that was selected */
  originalText: string;
  /** User's free-text annotation */
  text: string;
  createdAt: number;
  author?: string;
  feedbackStatus?: "pending" | "accepted" | "rejected";
  importedAt?: number;
}

export interface Block {
  id: string;
  type: "paragraph" | "heading" | "blockquote" | "list-item" | "code" | "hr" | "table";
  content: string;
  level?: number;
  language?: string;
  checked?: boolean;
  order: number;
  startLine: number;
}

