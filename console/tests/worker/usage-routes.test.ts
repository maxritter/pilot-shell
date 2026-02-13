/**
 * Tests for UsageRoutes
 *
 * Tests the /api/usage/* endpoints with mocked execFileSync calls.
 * Covers: daily/monthly/models endpoints, caching, date validation, missing ccusage.
 */
import { describe, it, expect, mock, beforeEach, afterEach } from "bun:test";

const mockExecFileSync = mock(() => "{}");

mock.module("child_process", () => ({
  execFileSync: mockExecFileSync,
}));

const originalBunWhich = Bun.which.bind(Bun);
let mockCcusagePath: string | null = "/usr/local/bin/ccusage";

import { UsageRoutes } from "../../src/services/worker/http/routes/UsageRoutes.js";

function createMockRes() {
  const res: any = {
    statusCode: 200,
    body: null,
    status(code: number) {
      res.statusCode = code;
      return res;
    },
    json(data: any) {
      res.body = data;
    },
  };
  return res;
}

function createMockReq(query: Record<string, string> = {}): any {
  return { query };
}

const SAMPLE_DAILY = JSON.stringify({
  daily: [
    {
      date: "2026-02-01",
      inputTokens: 100,
      outputTokens: 50,
      cacheCreationTokens: 500,
      cacheReadTokens: 700,
      totalTokens: 1350,
      totalCost: 3.45,
      modelsUsed: ["claude-opus-4-6"],
      modelBreakdowns: [
        { modelName: "claude-opus-4-6", inputTokens: 100, outputTokens: 50, cacheCreationTokens: 500, cacheReadTokens: 700, cost: 3.45 },
      ],
    },
  ],
});

const SAMPLE_MONTHLY = JSON.stringify({
  monthly: [
    {
      month: "2026-02",
      inputTokens: 1000,
      outputTokens: 500,
      cacheCreationTokens: 5000,
      cacheReadTokens: 7000,
      totalTokens: 13500,
      totalCost: 34.5,
      modelsUsed: ["claude-opus-4-6", "claude-sonnet-4-5-20250929"],
      modelBreakdowns: [
        { modelName: "claude-opus-4-6", inputTokens: 800, outputTokens: 400, cacheCreationTokens: 4000, cacheReadTokens: 6000, cost: 30.0 },
        { modelName: "claude-sonnet-4-5-20250929", inputTokens: 200, outputTokens: 100, cacheCreationTokens: 1000, cacheReadTokens: 1000, cost: 4.5 },
      ],
    },
  ],
});

describe("UsageRoutes", () => {
  let routes: UsageRoutes;

  beforeEach(() => {
    mockExecFileSync.mockReset();
    mockCcusagePath = "/usr/local/bin/ccusage";
    Bun.which = ((cmd: string) => (cmd === "ccusage" ? mockCcusagePath : originalBunWhich(cmd))) as typeof Bun.which;
    routes = new UsageRoutes();
  });

  afterEach(() => {
    Bun.which = originalBunWhich;
  });

  describe("route setup", () => {
    it("should register all usage routes", () => {
      const registeredRoutes: string[] = [];
      const mockApp = {
        get: (path: string) => registeredRoutes.push(`GET ${path}`),
      };

      routes.setupRoutes(mockApp as any);

      expect(registeredRoutes).toContain("GET /api/usage/daily");
      expect(registeredRoutes).toContain("GET /api/usage/monthly");
      expect(registeredRoutes).toContain("GET /api/usage/models");
    });
  });

  describe("GET /api/usage/daily", () => {
    it("should return daily usage data", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_DAILY);
      const req = createMockReq({ since: "20260201" });
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.body).toBeDefined();
      expect(res.body.available).toBe(true);
      expect(res.body.daily).toHaveLength(1);
      expect(res.body.daily[0].date).toBe("2026-02-01");
    });

    it("should reject invalid since parameter", async () => {
      const req = createMockReq({ since: "not-a-date" });
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.statusCode).toBe(400);
      expect(res.body.error).toContain("Invalid");
    });

    it("should reject invalid until parameter", async () => {
      const req = createMockReq({ until: "abc" });
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.statusCode).toBe(400);
      expect(res.body.error).toContain("Invalid");
    });

    it("should use default 30-day window when no since provided", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_DAILY);
      const req = createMockReq({});
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.body.available).toBe(true);
      expect(mockExecFileSync).toHaveBeenCalled();
    });
  });

  describe("GET /api/usage/monthly", () => {
    it("should return monthly usage data", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_MONTHLY);
      const req = createMockReq();
      const res = createMockRes();

      await routes.handleMonthly(req, res);

      expect(res.body).toBeDefined();
      expect(res.body.available).toBe(true);
      expect(res.body.monthly).toHaveLength(1);
      expect(res.body.monthly[0].month).toBe("2026-02");
    });
  });

  describe("GET /api/usage/models", () => {
    it("should aggregate model data from monthly endpoint", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_MONTHLY);
      const req = createMockReq();
      const res = createMockRes();

      await routes.handleModels(req, res);

      expect(res.body).toBeDefined();
      expect(res.body.available).toBe(true);
      expect(res.body.models).toBeDefined();
      expect(res.body.models).toHaveLength(2);
      const modelNames = res.body.models.map((m: any) => m.model);
      expect(modelNames).toContain("claude-opus-4-6");
      expect(modelNames).toContain("claude-sonnet-4-5-20250929");
      const opus = res.body.models.find((m: any) => m.model === "claude-opus-4-6");
      expect(opus.totalCost).toBe(30.0);
      expect(opus.totalTokens).toBe(800 + 400 + 4000 + 6000);
    });
  });

  describe("caching", () => {
    it("should cache results for 5 minutes", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_DAILY);
      const req = createMockReq({ since: "20260201" });
      const res1 = createMockRes();
      const res2 = createMockRes();

      await routes.handleDaily(req, res1);
      await routes.handleDaily(req, res2);

      expect(mockExecFileSync).toHaveBeenCalledTimes(1);
      expect(res2.body.available).toBe(true);
    });
  });

  describe("ccusage not installed", () => {
    it("should return available: false when ccusage is missing", async () => {
      mockCcusagePath = null;
      routes = new UsageRoutes();
      const req = createMockReq();
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.body.available).toBe(false);
      expect(res.body.error).toContain("not installed");
    });
  });

  describe("error recovery", () => {
    it("should allow retry after ccusage command fails", async () => {
      mockExecFileSync.mockImplementationOnce(() => { throw new Error("timeout"); });
      mockExecFileSync.mockReturnValueOnce(SAMPLE_DAILY);

      const req = createMockReq({ since: "20260201" });
      const res1 = createMockRes();

      try {
        await routes.handleDaily(req, res1);
      } catch {
      }

      const res2 = createMockRes();
      await routes.handleDaily(req, res2);

      expect(res2.body.available).toBe(true);
      expect(res2.body.daily).toHaveLength(1);
    });
  });

  describe("date validation", () => {
    it("should accept valid YYYYMMDD dates", async () => {
      mockExecFileSync.mockReturnValue(SAMPLE_DAILY);
      const req = createMockReq({ since: "20260101", until: "20260131" });
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.statusCode).toBe(200);
      expect(res.body.available).toBe(true);
    });

    it("should reject dates with special characters", async () => {
      const req = createMockReq({ since: "2026;rm -rf /" });
      const res = createMockRes();

      await routes.handleDaily(req, res);

      expect(res.statusCode).toBe(400);
    });
  });
});
