/**
 * Tests for Task 10: Spec view project filtering
 *
 * Validates:
 * - Spec view imports useProject from context
 * - Passes ?project= to /api/plans/active
 * - Passes ?project= to /api/plan/content
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";

const SPEC_PATH = path.join(
  __dirname,
  "../../src/ui/viewer/views/Spec/index.tsx",
);
const specSource = readFileSync(SPEC_PATH, "utf-8");

describe("Task 10: Spec view project filter", () => {
  it("should import useProject from context", () => {
    expect(specSource).toContain("useProject");
  });

  it("should pass project param to /api/plans/active", () => {
    expect(specSource).toMatch(/plans\/active.*project/);
  });

  it("should pass project param to /api/plan/content", () => {
    expect(specSource).toMatch(/plan\/content.*project/);
  });

  it("should destructure selectedProject from useProject", () => {
    expect(specSource).toContain("selectedProject");
  });
});
