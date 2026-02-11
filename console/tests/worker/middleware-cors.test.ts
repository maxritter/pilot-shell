/**
 * Tests for CORS localhost restriction in middleware
 *
 * Mock Justification:
 * - cors package: We test the origin callback function directly, not the cors middleware internals
 * - No network calls or external dependencies mocked
 */
import { describe, it, expect } from "bun:test";
import { isAllowedOrigin } from "../../src/services/worker/http/middleware.js";

describe("CORS localhost restriction", () => {
  describe("isAllowedOrigin", () => {
    it("should allow http://localhost with any port", () => {
      expect(isAllowedOrigin("http://localhost:41777")).toBe(true);
      expect(isAllowedOrigin("http://localhost:3000")).toBe(true);
      expect(isAllowedOrigin("http://localhost:8080")).toBe(true);
    });

    it("should allow http://localhost without port", () => {
      expect(isAllowedOrigin("http://localhost")).toBe(true);
    });

    it("should allow http://127.0.0.1 with any port", () => {
      expect(isAllowedOrigin("http://127.0.0.1:41777")).toBe(true);
      expect(isAllowedOrigin("http://127.0.0.1:3000")).toBe(true);
    });

    it("should allow http://127.0.0.1 without port", () => {
      expect(isAllowedOrigin("http://127.0.0.1")).toBe(true);
    });

    it("should allow http://[::1] with any port", () => {
      expect(isAllowedOrigin("http://[::1]:41777")).toBe(true);
      expect(isAllowedOrigin("http://[::1]:3000")).toBe(true);
    });

    it("should allow http://[::1] without port", () => {
      expect(isAllowedOrigin("http://[::1]")).toBe(true);
    });

    it("should reject requests from external origins", () => {
      expect(isAllowedOrigin("http://evil.com")).toBe(false);
      expect(isAllowedOrigin("https://attacker.example.com")).toBe(false);
      expect(isAllowedOrigin("http://192.168.1.100:3000")).toBe(false);
    });

    it("should allow undefined origin (non-browser clients like curl)", () => {
      expect(isAllowedOrigin(undefined)).toBe(true);
    });

    it("should reject origins that contain localhost but aren't localhost", () => {
      expect(isAllowedOrigin("http://localhost.evil.com")).toBe(false);
      expect(isAllowedOrigin("http://not-localhost:3000")).toBe(false);
    });

    it("should allow https://localhost variants", () => {
      expect(isAllowedOrigin("https://localhost:3000")).toBe(true);
      expect(isAllowedOrigin("https://127.0.0.1:8443")).toBe(true);
    });
  });
});
