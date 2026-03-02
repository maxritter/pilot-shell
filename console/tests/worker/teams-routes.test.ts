/**
 * TeamsRoutes Tests
 *
 * Tests for the Teams status and install API endpoints.
 * Validates caching, timeout handling, concurrency protection, and error cases.
 */

import { describe, it, expect } from "bun:test";
import { TeamsRoutes, type TeamsStatusResponse } from "../../src/services/worker/http/routes/TeamsRoutes.js";

describe("TeamsRoutes", () => {
  describe("class structure", () => {
    it("can be instantiated", () => {
      const routes = new TeamsRoutes();
      expect(routes).toBeDefined();
      expect(routes).toBeInstanceOf(TeamsRoutes);
    });

    it("registers all 8 routes", () => {
      const routes = new TeamsRoutes();
      const registered: { method: string; path: string }[] = [];
      const fakeApp = {
        get: (path: string, _handler: any) => registered.push({ method: "GET", path }),
        post: (path: string, _handler: any) => registered.push({ method: "POST", path }),
      };
      routes.setupRoutes(fakeApp as any);

      expect(registered).toContainEqual({ method: "GET", path: "/api/teams/status" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/teams/install" });
      expect(registered).toContainEqual({ method: "GET", path: "/api/teams/detail/:name" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/teams/push" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/teams/remove" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/teams/init" });
      expect(registered).toContainEqual({ method: "GET", path: "/api/teams/discover" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/teams/update-asset" });
      expect(registered.length).toBe(8);
    });
  });

  describe("push endpoint behavior", () => {
    it("returns 400 for missing required fields", async () => {
      const routes = new TeamsRoutes();
      let pushHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/push") pushHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await pushHandler({ body: { source: "path", type: "skill" } }, fakeRes);
      expect(statusCode).toBe(400);
      expect(responseData.error).toContain("required");
    });

    it("returns 400 for invalid asset name", async () => {
      const routes = new TeamsRoutes();
      let pushHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/push") pushHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await pushHandler({ body: { source: "path", type: "skill", name: "bad name!" } }, fakeRes);
      expect(statusCode).toBe(400);
      expect(responseData.error).toContain("Invalid asset name");
    });

    it("returns 400 for path outside project root", async () => {
      const routes = new TeamsRoutes();
      let pushHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/push") pushHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      (routes as any).resolveSxBinary = () => null;
      await pushHandler({ body: { source: "../../etc/passwd", type: "rule", name: "bad-path" } }, fakeRes);
      expect(statusCode).toBe(400);
      expect(responseData.error).toContain("project");
    });
  });

  describe("remove endpoint behavior", () => {
    it("returns 400 for invalid asset name", async () => {
      const routes = new TeamsRoutes();
      let removeHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/remove") removeHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await removeHandler({ body: { name: "bad name!" } }, fakeRes);
      expect(statusCode).toBe(400);
    });

    it("returns success when sx remove succeeds", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => "";

      let removeHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/remove") removeHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let responseData: any;
      const fakeRes = { json: (data: any) => { responseData = data; }, status: () => fakeRes };

      await removeHandler({ body: { name: "my-skill" } }, fakeRes);
      expect(responseData.success).toBe(true);
    });
  });

  describe("init endpoint behavior", () => {
    it("returns 400 for missing fields", async () => {
      const routes = new TeamsRoutes();
      let initHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/init") initHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: () => {},
      };

      await initHandler({ body: { type: "git" } }, fakeRes);
      expect(statusCode).toBe(400);
    });
  });

  describe("discover endpoint behavior", () => {
    it("returns assets array and repoUrl", async () => {
      const routes = new TeamsRoutes();
      const handlers: Record<string, any> = {};
      const fakeApp = {
        get: (p: string, handler: any) => { handlers[p] = handler; },
        post: (p: string, handler: any) => { handlers[p] = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      const discoverHandler = handlers["/api/teams/discover"];
      expect(discoverHandler).toBeDefined();

      let responseData: any;
      const fakeRes = { json: (data: any) => { responseData = data; }, status: () => fakeRes };

      discoverHandler({}, fakeRes);
      await new Promise((r) => setTimeout(r, 50));

      expect(responseData).toBeDefined();
      expect(Array.isArray(responseData.assets)).toBe(true);
      expect("repoUrl" in responseData).toBe(true);
    });
  });

  describe("emptyStatus", () => {
    it("returns correct empty status shape", () => {
      const status: TeamsStatusResponse = {
        installed: false,
        version: null,
        configured: false,
        repoUrl: null,
        profile: null,
        assets: [],
        catalog: [],
        isInstalling: false,
      };

      expect(status.installed).toBe(false);
      expect(status.version).toBeNull();
      expect(status.configured).toBe(false);
      expect(status.repoUrl).toBeNull();
      expect(status.profile).toBeNull();
      expect(status.assets).toEqual([]);
      expect(status.catalog).toEqual([]);
      expect(status.isInstalling).toBe(false);
    });
  });

  describe("TeamsStatusResponse type", () => {
    it("accepts valid asset array", () => {
      const status: TeamsStatusResponse = {
        installed: true,
        version: "1.2.3",
        configured: true,
        repoUrl: "git@github.com:org/vault.git",
        profile: "default",
        assets: [
          {
            name: "my-rule",
            version: "v3",
            type: "rule",
            clients: ["project-a"],
            status: "installed",
            scope: "Global",
          },
        ],
        catalog: [
          {
            name: "my-rule",
            type: "rule",
            latestVersion: "v3",
            versionsCount: 3,
            updatedAt: "2026-02-12",
          },
        ],
        isInstalling: false,
      };

      expect(status.installed).toBe(true);
      expect(status.assets).toHaveLength(1);
      expect(status.assets[0].name).toBe("my-rule");
      expect(status.catalog).toHaveLength(1);
      expect(status.catalog[0].versionsCount).toBe(3);
    });

    it("handles multiple assets with different scopes", () => {
      const status: TeamsStatusResponse = {
        installed: true,
        version: "2.0.0",
        configured: true,
        repoUrl: "https://github.com/org/vault",
        profile: "team",
        assets: [
          { name: "rule-a", version: "v1", type: "rule", clients: [], status: "installed", scope: "Global" },
          { name: "skill-b", version: "v2", type: "skill", clients: ["repo1"], status: "installed", scope: "repo1" },
          { name: "hook-c", version: "v1", type: "hook", clients: ["repo1", "repo2"], status: "installed", scope: "Global" },
        ],
        catalog: [],
        isInstalling: false,
      };

      expect(status.assets).toHaveLength(3);
      const scopes = status.assets.map((a: { scope: string }) => a.scope);
      expect(scopes).toContain("Global");
      expect(scopes).toContain("repo1");
    });
  });

  describe("status endpoint behavior", () => {
    it("returns empty status when sx binary is not found", async () => {
      const routes = new TeamsRoutes();
      let responseData: any;
      const fakeRes = {
        json: (data: any) => { responseData = data; },
        status: () => fakeRes,
      };
      const fakeReq = {};

      let statusHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => { if (path === "/api/teams/status") statusHandler = handler; },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      (routes as any).resolveSxBinary = () => null;

      await statusHandler(fakeReq, fakeRes);

      expect(responseData).toBeDefined();
      expect(responseData.installed).toBe(false);
      expect(responseData.assets).toEqual([]);
      expect(responseData.catalog).toEqual([]);
    });

    it("returns cached status on second call within TTL", async () => {
      const routes = new TeamsRoutes();

      const cachedStatus: TeamsStatusResponse = {
        installed: true, version: "1.0", configured: true,
        repoUrl: "https://repo", profile: null,
        assets: [], catalog: [], isInstalling: false,
      };
      (routes as any).statusCache = { data: cachedStatus, timestamp: Date.now() };

      let statusHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => { if (path === "/api/teams/status") statusHandler = handler; },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let responseData: any;
      const fakeRes = { json: (data: any) => { responseData = data; }, status: () => fakeRes };

      statusHandler({}, fakeRes);
      await new Promise((r) => setTimeout(r, 20));

      expect(responseData.installed).toBe(true);
      expect(responseData.version).toBe("1.0");
    });

    it("fetches fresh status when cache is expired", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async (args: string[]) => {
        if (args.includes("config")) {
          return JSON.stringify({ version: { version: "2.0" }, config: { repositoryUrl: "https://new" }, assets: [] });
        }
        return "[]";
      };
      (routes as any).statusCache = { data: { installed: true, version: "1.0" }, timestamp: 0 };

      let statusHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => { if (path === "/api/teams/status") statusHandler = handler; },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let responseData: any;
      const fakeRes = { json: (data: any) => { responseData = data; }, status: () => fakeRes };

      statusHandler({}, fakeRes);
      await new Promise((r) => setTimeout(r, 50));

      expect(responseData.installed).toBe(true);
      expect(responseData.version).toBe("2.0");
    });

    it("returns empty status on JSON parse failure", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => "not-json";

      let statusHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => { if (path === "/api/teams/status") statusHandler = handler; },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let responseData: any;
      const fakeRes = {
        json: (data: any) => { responseData = data; },
        status: () => fakeRes,
      };

      statusHandler({}, fakeRes);
      await new Promise((r) => setTimeout(r, 50));

      expect(responseData).toBeDefined();
      expect(responseData.installed).toBe(false);
    });
  });

  describe("install endpoint behavior", () => {
    it("returns 409 when installation already in progress", async () => {
      const routes = new TeamsRoutes();
      (routes as any)._isInstalling = true;

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/install") installHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await installHandler({}, fakeRes);
      expect(statusCode).toBe(409);
      expect(responseData.error).toContain("already in progress");
    });

    it("returns 500 when sx binary is not found", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => null;

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/install") installHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await installHandler({}, fakeRes);
      expect(statusCode).toBe(500);
      expect(responseData.error).toContain("not found");
    });

    it("clears cache and resets isInstalling after install completes", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => "";

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/install") installHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      const fakeRes = {
        status: () => fakeRes,
        json: () => {},
      };

      (routes as any).statusCache = { data: {}, timestamp: Date.now() };

      await installHandler({}, fakeRes);

      await new Promise((resolve) => setTimeout(resolve, 50));

      expect((routes as any)._isInstalling).toBe(false);
      expect((routes as any).statusCache).toBeNull();
      expect((routes as any).detailCache.size).toBe(0);
    });

    it("passes --target with project root to install command", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      let capturedArgs: string[] = [];
      (routes as any).runSxCommand = async (args: string[]) => { capturedArgs = args; return ""; };

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/install") installHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      const fakeRes = {
        status: () => fakeRes,
        json: () => {},
      };

      await installHandler({}, fakeRes);
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(capturedArgs).toContain("--target");
      expect(capturedArgs).toContain("--repair");
      const targetIdx = capturedArgs.indexOf("--target");
      expect(targetIdx).toBeGreaterThan(-1);
      expect(capturedArgs[targetIdx + 1]).toBeDefined();
    });

    it("resets isInstalling even when install fails", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => { throw new Error("install failed"); };

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (p: string, handler: any) => { if (p === "/api/teams/install") installHandler = handler; },
      };
      routes.setupRoutes(fakeApp as any);

      const fakeRes = {
        status: () => fakeRes,
        json: () => {},
      };

      await installHandler({}, fakeRes);
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect((routes as any)._isInstalling).toBe(false);
    });
  });

  describe("detail endpoint behavior", () => {
    it("returns asset detail with version history for valid name", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async (args: string[]) => {
        if (args.includes("vault") && args.includes("show")) {
          return JSON.stringify({
            name: "lsp-cleaner",
            type: "skill",
            metadata: {
              description: "Clean up unused code",
              authors: ["test"],
            },
            versions: [
              { version: "3", createdAt: "2026-02-14", filesCount: 5 },
              { version: "2", createdAt: "2026-02-10", filesCount: 4 },
              { version: "1", createdAt: "2026-02-01", filesCount: 3 },
            ],
          });
        }
        return "{}";
      };

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let responseData: any;
      const fakeReq = { params: { name: "lsp-cleaner" } };
      const fakeRes = {
        json: (data: any) => { responseData = data; },
        status: () => fakeRes,
      };

      await detailHandler(fakeReq, fakeRes);

      expect(responseData).toBeDefined();
      expect(responseData.name).toBe("lsp-cleaner");
      expect(responseData.type).toBe("skill");
      expect(responseData.metadata?.description).toBe("Clean up unused code");
      expect(responseData.versions).toHaveLength(3);
      expect(responseData.versions[0].version).toBe("3");
    });

    it("returns 400 for asset name with special characters", async () => {
      const routes = new TeamsRoutes();

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeReq = { params: { name: "lsp-cleaner; rm -rf /" } };
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await detailHandler(fakeReq, fakeRes);

      expect(statusCode).toBe(400);
      expect(responseData.error).toContain("Invalid asset name");
    });

    it("returns 404 for nonexistent asset", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => {
        throw new Error("sx exited with code 1: Asset not found");
      };

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeReq = { params: { name: "nonexistent" } };
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await detailHandler(fakeReq, fakeRes);

      expect(statusCode).toBe(404);
      expect(responseData.error).toContain("not found");
    });

    it("returns 502 for malformed sx output", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => {
        return JSON.stringify({ type: "skill" });
      };

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeReq = { params: { name: "test-asset" } };
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await detailHandler(fakeReq, fakeRes);

      expect(statusCode).toBe(502);
      expect(responseData.error).toContain("Unexpected sx response format");
    });

    it("caches detail responses for 60s", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      let callCount = 0;
      (routes as any).runSxCommand = async () => {
        callCount++;
        return JSON.stringify({
          name: "test-asset",
          type: "rule",
          versions: [{ version: "1", createdAt: "2026-02-14", filesCount: 2 }],
        });
      };

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      const fakeReq = { params: { name: "test-asset" } };
      const fakeRes = {
        json: () => {},
        status: () => fakeRes,
      };

      await detailHandler(fakeReq, fakeRes);
      await detailHandler(fakeReq, fakeRes);

      expect(callCount).toBe(1);
    });

    it("returns 500 when sx binary is not found", async () => {
      const routes = new TeamsRoutes();
      (routes as any).resolveSxBinary = () => null;

      let detailHandler: any;
      const fakeApp = {
        get: (path: string, handler: any) => {
          if (path === "/api/teams/detail/:name") detailHandler = handler;
        },
        post: () => {},
      };
      routes.setupRoutes(fakeApp as any);

      let statusCode = 200;
      let responseData: any;
      const fakeReq = { params: { name: "test-asset" } };
      const fakeRes = {
        status: (code: number) => { statusCode = code; return fakeRes; },
        json: (data: any) => { responseData = data; },
      };

      await detailHandler(fakeReq, fakeRes);

      expect(statusCode).toBe(500);
      expect(responseData.error).toContain("sx CLI not found");
    });
  });
});
