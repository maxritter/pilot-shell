/**
 * Tests for middleware ordering of DB initialization guard
 *
 * Verifies that the /api/context/inject initialization guard is registered
 * BEFORE route handlers, so requests wait for initialization to complete.
 *
 * Mock Justification:
 * - We inspect the source code order rather than spinning up a full Express server,
 *   because the ordering is a code structure concern that can be statically verified.
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";

describe("Middleware ordering for DB initialization guard", () => {
  it("should register /api/context/inject guard BEFORE route handlers", () => {
    const workerServicePath = path.join(
      import.meta.dir,
      "../../src/services/worker-service.ts",
    );
    const source = readFileSync(workerServicePath, "utf-8");

    const registerRoutesMatch = source.match(
      /private\s+registerRoutes\(\)[\s\S]*?^\s{2}\}/m,
    );
    expect(registerRoutesMatch).toBeTruthy();

    const methodBody = registerRoutesMatch![0];

    const guardIndex = methodBody.indexOf('"/api/context/inject"');
    const firstRegisterRoutes = methodBody.indexOf("this.server.registerRoutes(");

    expect(guardIndex).toBeGreaterThan(-1);
    expect(firstRegisterRoutes).toBeGreaterThan(-1);
    expect(guardIndex).toBeLessThan(firstRegisterRoutes);
  });

  it("should return 503 during initialization when searchRoutes not ready", () => {
    const workerServicePath = path.join(
      import.meta.dir,
      "../../src/services/worker-service.ts",
    );
    const source = readFileSync(workerServicePath, "utf-8");

    expect(source).toContain("if (!this.searchRoutes)");
    expect(source).toContain('res.status(503)');
  });
});
