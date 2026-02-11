import DOMPurify from "isomorphic-dompurify";

/** Sanitize HTML to prevent XSS attacks while preserving safe ANSI-converted markup. */
export function sanitizeHtml(html: string): string {
  if (!html) return "";
  return DOMPurify.sanitize(html);
}
