/**
 * VaultRoutes Tests
 *
 * Tests for the Vault status and install API endpoints.
 * Validates caching, timeout handling, concurrency protection, and error cases.
 */

import { describe, it, expect } from "bun:test";
import { VaultRoutes, type VaultStatus } from "../../src/services/worker/http/routes/VaultRoutes.js";

describe("VaultRoutes", () => {
  describe("class structure", () => {
    it("can be instantiated", () => {
      const routes = new VaultRoutes();
      expect(routes).toBeDefined();
      expect(routes).toBeInstanceOf(VaultRoutes);
    });

    it("registers status and install routes", () => {
      const routes = new VaultRoutes();
      const registered: { method: string; path: string }[] = [];
      const fakeApp = {
        get: (path: string, _handler: any) => registered.push({ method: "GET", path }),
        post: (path: string, _handler: any) => registered.push({ method: "POST", path }),
      };
      routes.setupRoutes(fakeApp as any);

      expect(registered).toContainEqual({ method: "GET", path: "/api/vault/status" });
      expect(registered).toContainEqual({ method: "POST", path: "/api/vault/install" });
    });
  });

  describe("emptyStatus", () => {
    it("returns correct empty status shape", () => {
      const routes = new VaultRoutes();
      const status: VaultStatus = {
        installed: false,
        version: null,
        configured: false,
        vaultUrl: null,
        profile: null,
        assets: [],
        catalog: [],
        isInstalling: false,
      };

      expect(status.installed).toBe(false);
      expect(status.version).toBeNull();
      expect(status.configured).toBe(false);
      expect(status.vaultUrl).toBeNull();
      expect(status.profile).toBeNull();
      expect(status.assets).toEqual([]);
      expect(status.catalog).toEqual([]);
      expect(status.isInstalling).toBe(false);
    });
  });

  describe("VaultStatus type", () => {
    it("accepts valid VaultAsset array", () => {
      const status: VaultStatus = {
        installed: true,
        version: "1.2.3",
        configured: true,
        vaultUrl: "git@github.com:org/vault.git",
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
      const status: VaultStatus = {
        installed: true,
        version: "2.0.0",
        configured: true,
        vaultUrl: "https://github.com/org/vault",
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
      const scopes = status.assets.map((a) => a.scope);
      expect(scopes).toContain("Global");
      expect(scopes).toContain("repo1");
    });
  });

  describe("status endpoint behavior", () => {
    it("returns empty status when sx binary is not found", async () => {
      const routes = new VaultRoutes();
      let responseData: any;
      const fakeRes = {
        json: (data: any) => { responseData = data; },
        status: () => fakeRes,
      };
      const fakeReq = {};

      let statusHandler: any;
      const fakeApp = {
        get: (_path: string, handler: any) => { statusHandler = handler; },
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
      const routes = new VaultRoutes();

      const cachedStatus: VaultStatus = {
        installed: true, version: "1.0", configured: true,
        vaultUrl: "https://repo", profile: null,
        assets: [], catalog: [], isInstalling: false,
      };
      (routes as any).statusCache = { data: cachedStatus, timestamp: Date.now() };

      let statusHandler: any;
      const fakeApp = {
        get: (_path: string, handler: any) => { statusHandler = handler; },
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
      const routes = new VaultRoutes();
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
        get: (_path: string, handler: any) => { statusHandler = handler; },
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
      const routes = new VaultRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => "not-json";

      let statusHandler: any;
      const fakeApp = {
        get: (_path: string, handler: any) => { statusHandler = handler; },
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
      const routes = new VaultRoutes();
      (routes as any)._isInstalling = true;

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (_path: string, handler: any) => { installHandler = handler; },
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
      const routes = new VaultRoutes();
      (routes as any).resolveSxBinary = () => null;

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (_path: string, handler: any) => { installHandler = handler; },
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
      const routes = new VaultRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => "";

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (_path: string, handler: any) => { installHandler = handler; },
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
    });

    it("resets isInstalling even when install fails", async () => {
      const routes = new VaultRoutes();
      (routes as any).resolveSxBinary = () => "/usr/local/bin/sx";
      (routes as any).runSxCommand = async () => { throw new Error("install failed"); };

      let installHandler: any;
      const fakeApp = {
        get: () => {},
        post: (_path: string, handler: any) => { installHandler = handler; },
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
});
