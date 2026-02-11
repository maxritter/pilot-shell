/**
 * Tests that worker-service.ts does not call getSessionStore() before dbManager.initialize()
 *
 * Mock Justification: Code-inspection pattern (readFileSync + string assertions)
 * Prevents regression where getSessionStore() was called in start() before
 * initializeBackground() had a chance to call dbManager.initialize(), causing
 * "Database not initialized" crash on startup.
 *
 * Value: Prevents silent startup crash that is hard to diagnose (process.exit(0) in catch)
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";

const WORKER_SERVICE_PATH = path.resolve(
  import.meta.dir,
  "../../src/services/worker-service.ts",
);

describe("worker-service database initialization order", () => {
  const source = readFileSync(WORKER_SERVICE_PATH, "utf-8");

  it("should not call getSessionStore() in start() before initializeBackground()", () => {
    const startMatch = source.match(
      /async start\(\): Promise<void>\s*\{([\s\S]*?)^\s{2}\}/m,
    );
    expect(startMatch).not.toBeNull();
    const startBody = startMatch![1];

    expect(startBody).not.toContain("getSessionStore()");
  });

  it("should call dbManager.initialize() before getSessionStore() in initializeBackground()", () => {
    const initMatch = source.match(
      /initializeBackground\(\): Promise<void>\s*\{([\s\S]*?)^\s{2}\}/m,
    );
    expect(initMatch).not.toBeNull();
    const initBody = initMatch![1];

    const initializeIdx = initBody.indexOf("dbManager.initialize()");
    const getStoreIdx = initBody.indexOf("getSessionStore()");

    expect(initializeIdx).toBeGreaterThan(-1);
    expect(getStoreIdx).toBeGreaterThan(-1);
    expect(initializeIdx).toBeLessThan(getStoreIdx);
  });
});
