/**
 * Tests for DOMPurify XSS defense in TerminalPreview
 *
 * Tests the sanitizeHtml function directly - it must strip dangerous tags
 * while preserving legitimate ANSI-converted HTML (spans with style attributes).
 */
import { describe, it, expect } from "bun:test";
import { sanitizeHtml } from "../../src/ui/viewer/utils/sanitize.js";

describe("TerminalPreview XSS defense", () => {
  describe("sanitizeHtml", () => {
    it("should strip script tags", () => {
      const malicious = '<script>alert("xss")</script>Hello';
      const result = sanitizeHtml(malicious);
      expect(result).not.toContain("<script");
      expect(result).toContain("Hello");
    });

    it("should strip onerror attributes", () => {
      const malicious = '<img src=x onerror="alert(1)">';
      const result = sanitizeHtml(malicious);
      expect(result).not.toContain("onerror");
    });

    it("should preserve span elements with style attributes from ANSI conversion", () => {
      const ansiHtml = '<span style="color:#ff0000">red text</span>';
      const result = sanitizeHtml(ansiHtml);
      expect(result).toContain("<span");
      expect(result).toContain("style");
      expect(result).toContain("red text");
    });

    it("should preserve nested span elements from ANSI conversion", () => {
      const ansiHtml =
        '<span style="color:#00ff00"><span style="font-weight:bold">bold green</span></span>';
      const result = sanitizeHtml(ansiHtml);
      expect(result).toContain("bold green");
      expect(result).toContain("<span");
    });

    it("should return empty string for empty input", () => {
      expect(sanitizeHtml("")).toBe("");
    });

    it("should pass through plain text unchanged", () => {
      expect(sanitizeHtml("hello world")).toBe("hello world");
    });

    it("should strip iframe tags", () => {
      const malicious = '<iframe src="http://evil.com"></iframe>text';
      const result = sanitizeHtml(malicious);
      expect(result).not.toContain("<iframe");
      expect(result).toContain("text");
    });
  });
});
