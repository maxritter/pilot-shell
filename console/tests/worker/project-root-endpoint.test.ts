/**
 * Tests for Task 4: /api/project-roots endpoint and workspaceProject in stats
 *
 * Validates:
 * - GET /api/project-roots endpoint registration
 * - Handler calls getAllProjectRoots() and returns results
 * - /api/stats includes worker.workspaceProject field
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";

const ROUTES_DIR = path.join(__dirname, "../../src/services/worker/http/routes");
const DATA_ROUTES_PATH = path.join(ROUTES_DIR, "DataRoutes.ts");
const dataRoutesSource = readFileSync(DATA_ROUTES_PATH, "utf-8");

describe("Task 4: /api/project-roots endpoint", () => {
  describe("Route Registration", () => {
    it("should register GET /api/project-roots endpoint", () => {
      expect(dataRoutesSource).toContain('"/api/project-roots"');
      expect(dataRoutesSource).toContain("handleGetProjectRoots");
    });

    it("should bind handleGetProjectRoots in setupRoutes", () => {
      const setupRoutesMatch = dataRoutesSource.match(
        /setupRoutes[\s\S]*?{([\s\S]*?)^\s{2}}/m,
      );
      expect(setupRoutesMatch).toBeTruthy();
      const setupBody = setupRoutesMatch![1];
      expect(setupBody).toContain("project-roots");
    });
  });

  describe("handleGetProjectRoots handler", () => {
    it("should call getAllProjectRoots from SessionStore", () => {
      expect(dataRoutesSource).toContain("getAllProjectRoots");
    });

    it("should return roots in response JSON", () => {
      expect(dataRoutesSource).toMatch(/roots/);
    });
  });
});

describe("Task 4: workspaceProject in /api/stats", () => {
  it("should include workspaceProject in handleGetStats response", () => {
    expect(dataRoutesSource).toContain("workspaceProject");
  });

  it("should derive workspaceProject from CLAUDE_PROJECT_ROOT or cwd()", () => {
    expect(dataRoutesSource).toMatch(/path\.basename/);
    expect(dataRoutesSource).toContain("CLAUDE_PROJECT_ROOT");
  });

  it("should include workspaceProject in the worker section of stats", () => {
    const workerSection = dataRoutesSource.match(
      /worker:\s*{([\s\S]*?)}/,
    );
    expect(workerSection).toBeTruthy();
    expect(workerSection![1]).toContain("workspaceProject");
  });
});
