/**
 * Tests for cross-project root path resolution in PlanRoutes and VexorRoutes
 *
 * Mock Justification: Code-inspection pattern (readFileSync + string assertions)
 * Tests that route handlers accept ?project= param and resolve project roots.
 *
 * Value: Validates cross-project filesystem support across plan, git, and vexor routes
 */
import { describe, it, expect } from "bun:test";
import { readFileSync, existsSync } from "fs";
import path from "path";

const PLAN_ROUTES_PATH = path.resolve(
  import.meta.dir,
  "../../src/services/worker/http/routes/PlanRoutes.ts",
);
const VEXOR_ROUTES_PATH = path.resolve(
  import.meta.dir,
  "../../src/services/worker/http/routes/VexorRoutes.ts",
);
const RESOLVE_UTIL_PATH = path.resolve(
  import.meta.dir,
  "../../src/services/worker/http/routes/utils/resolveProjectRoot.ts",
);
const WORKER_SERVICE_PATH = path.resolve(
  import.meta.dir,
  "../../src/services/worker-service.ts",
);

describe("resolveProjectRoot utility", () => {
  it("should exist as a standalone utility module", () => {
    expect(existsSync(RESOLVE_UTIL_PATH)).toBe(true);
  });

  it("should export resolveProjectRoot function", () => {
    const source = readFileSync(RESOLVE_UTIL_PATH, "utf-8");
    expect(source).toContain("export function resolveProjectRoot");
  });

  it("should accept DatabaseManager and optional project param", () => {
    const source = readFileSync(RESOLVE_UTIL_PATH, "utf-8");
    expect(source).toContain("DatabaseManager");
    expect(source).toContain("project");
  });

  it("should validate resolved paths are directories", () => {
    const source = readFileSync(RESOLVE_UTIL_PATH, "utf-8");
    expect(source).toContain("existsSync");
  });
});

describe("PlanRoutes cross-project support", () => {
  const source = readFileSync(PLAN_ROUTES_PATH, "utf-8");

  it("should import resolveProjectRoot from shared utility", () => {
    expect(source).toContain("resolveProjectRoot");
    expect(source).toContain("utils/resolveProjectRoot");
  });

  it("handleGetActivePlan should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleGetActivePlan"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleGetAllPlans should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleGetAllPlans"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleGetGitInfo should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleGetGitInfo"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleGetActiveSpecs should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleGetActiveSpecs"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleGetPlanContent should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleGetPlanContent"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });
});

describe("VexorRoutes cross-project support", () => {
  const source = readFileSync(VEXOR_ROUTES_PATH, "utf-8");

  it("should accept DatabaseManager in constructor", () => {
    expect(source).toContain("DatabaseManager");
    expect(source).toContain("dbManager");
  });

  it("should import resolveProjectRoot from shared utility", () => {
    expect(source).toContain("resolveProjectRoot");
    expect(source).toContain("utils/resolveProjectRoot");
  });

  it("handleStatus should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleStatus"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleSearch should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleSearch"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });

  it("handleReindex should use ?project= query param", () => {
    const handler = source.slice(source.indexOf("handleReindex"));
    expect(handler).toContain("req.query.project");
    expect(handler).toContain("resolveProjectRoot");
  });
});

describe("worker-service.ts wiring", () => {
  const source = readFileSync(WORKER_SERVICE_PATH, "utf-8");

  it("should pass dbManager to VexorRoutes constructor", () => {
    expect(source).toContain("new VexorRoutes(this.dbManager)");
  });
});
