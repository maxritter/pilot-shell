/**
 * Tests for WorktreeRoutes
 *
 * Tests the worktree status detection and diff parsing logic.
 * Git commands are tested via their output parsing, not by running real git.
 */
import { describe, it, expect } from "bun:test";
import { WorktreeRoutes } from "../../src/services/worker/http/routes/WorktreeRoutes.js";

describe("WorktreeRoutes", () => {
  describe("countFilesFromStat", () => {
    it("should parse file count from git diff --stat output", () => {
      const routes = new WorktreeRoutes();
      const count = (routes as any).countFilesFromStat(
        " src/main.ts | 10 ++++\n src/util.ts | 5 ++---\n 2 files changed, 12 insertions(+), 3 deletions(-)\n",
      );
      expect(count).toBe(2);
    });

    it("should return 0 for empty output", () => {
      const routes = new WorktreeRoutes();
      const count = (routes as any).countFilesFromStat("");
      expect(count).toBe(0);
    });

    it("should handle single file changed", () => {
      const routes = new WorktreeRoutes();
      const count = (routes as any).countFilesFromStat(
        " src/main.ts | 10 ++++\n 1 file changed, 10 insertions(+)\n",
      );
      expect(count).toBe(1);
    });
  });

  describe("parseChangedFiles", () => {
    it("should parse name-status and numstat into file change list", () => {
      const routes = new WorktreeRoutes();
      const nameStatus = "A\tsrc/new-file.ts\nM\tsrc/existing.ts\nD\tsrc/removed.ts\n";
      const numstat = "50\t0\tsrc/new-file.ts\n10\t5\tsrc/existing.ts\n0\t30\tsrc/removed.ts\n";

      const files = routes.parseChangedFiles(nameStatus, numstat);

      expect(files).toHaveLength(3);
      expect(files[0]).toEqual({ path: "src/new-file.ts", status: "A", additions: 50, deletions: 0 });
      expect(files[1]).toEqual({ path: "src/existing.ts", status: "M", additions: 10, deletions: 5 });
      expect(files[2]).toEqual({ path: "src/removed.ts", status: "D", additions: 0, deletions: 30 });
    });

    it("should return empty array for empty output", () => {
      const routes = new WorktreeRoutes();
      const files = routes.parseChangedFiles("", "");
      expect(files).toEqual([]);
    });

    it("should handle name-status without matching numstat", () => {
      const routes = new WorktreeRoutes();
      const nameStatus = "A\tsrc/new-file.ts\n";
      const numstat = "";

      const files = routes.parseChangedFiles(nameStatus, numstat);

      expect(files).toHaveLength(1);
      expect(files[0]).toEqual({ path: "src/new-file.ts", status: "A", additions: 0, deletions: 0 });
    });

    it("should handle renamed files (R status)", () => {
      const routes = new WorktreeRoutes();
      const nameStatus = "R100\tsrc/old.ts\tsrc/new.ts\n";
      const numstat = "0\t0\tsrc/new.ts\n";

      const files = routes.parseChangedFiles(nameStatus, numstat);

      expect(files).toHaveLength(1);
      expect(files[0].status).toBe("R");
      expect(files[0].path).toBe("src/new.ts");
    });
  });

  describe("route setup", () => {
    it("should register all expected routes", () => {
      const routes = new WorktreeRoutes();
      const registeredRoutes: string[] = [];

      const mockApp = {
        get: (path: string) => registeredRoutes.push(`GET ${path}`),
        post: (path: string) => registeredRoutes.push(`POST ${path}`),
      };

      routes.setupRoutes(mockApp as any);

      expect(registeredRoutes).toContain("GET /api/worktree/status");
      expect(registeredRoutes).toContain("GET /api/worktree/diff");
      expect(registeredRoutes).toContain("GET /api/worktree/diff/:file(*)");
      expect(registeredRoutes).toContain("POST /api/worktree/sync");
      expect(registeredRoutes).toContain("POST /api/worktree/discard");
    });
  });
});
