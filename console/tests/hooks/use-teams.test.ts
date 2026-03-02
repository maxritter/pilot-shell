/**
 * useTeams Hook Tests
 *
 * Tests for the teams hook's data merging logic, version comparison,
 * and interface contract.
 */

import { describe, it, expect } from "bun:test";
import { renderToString } from "react-dom/server";
import React from "react";

describe("useTeams", () => {
  it("hook is exported", async () => {
    const mod = await import("../../src/ui/viewer/hooks/useTeams.js");
    expect(mod.useTeams).toBeDefined();
    expect(typeof mod.useTeams).toBe("function");
  });

  it("mergeAssets is exported as a pure function", async () => {
    const mod = await import("../../src/ui/viewer/hooks/useTeams.js");
    expect(mod.mergeAssets).toBeDefined();
    expect(typeof mod.mergeAssets).toBe("function");
  });

  it("returns expected interface via SSR", async () => {
    const { useTeams } = await import("../../src/ui/viewer/hooks/useTeams.js");

    function TestComponent() {
      const result = useTeams();
      return React.createElement(
        "div",
        null,
        `loading:${result.isLoading}`,
        `|assets:${result.mergedAssets.length}`,
        `|installing:${result.isInstalling}`,
      );
    }

    const html = renderToString(React.createElement(TestComponent));
    expect(html).toContain("loading:");
    expect(html).toContain("assets:");
    expect(html).toContain("installing:");
  });

  describe("mergeAssets", () => {
    it("marks catalog-only items as not installed", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "my-rule", type: "rule", latestVersion: "3", versionsCount: 3, updatedAt: "2026-02-14" },
      ];
      const assets: any[] = [];

      const result = mergeAssets(catalog, assets);

      expect(result).toHaveLength(1);
      expect(result[0].name).toBe("my-rule");
      expect(result[0].installed).toBe(false);
      expect(result[0].installedVersion).toBeNull();
      expect(result[0].hasUpdate).toBe(false);
    });

    it("marks installed item with matching version as no update", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "my-rule", type: "rule", latestVersion: "3", versionsCount: 3, updatedAt: "2026-02-14" },
      ];
      const assets = [
        { name: "my-rule", version: "v3", type: "rule", clients: ["repo1"], status: "installed", scope: "Global" },
      ];

      const result = mergeAssets(catalog, assets);

      expect(result).toHaveLength(1);
      expect(result[0].installed).toBe(true);
      expect(result[0].installedVersion).toBe("v3");
      expect(result[0].hasUpdate).toBe(false);
      expect(result[0].scope).toBe("Global");
      expect(result[0].clients).toEqual(["repo1"]);
    });

    it("detects update when installed version < latest version (integer comparison)", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "my-skill", type: "skill", latestVersion: "5", versionsCount: 5, updatedAt: "2026-02-14" },
      ];
      const assets = [
        { name: "my-skill", version: "v2", type: "skill", clients: [], status: "installed", scope: "Global" },
      ];

      const result = mergeAssets(catalog, assets);

      expect(result[0].hasUpdate).toBe(true);
    });

    it("returns hasUpdate=false when versions cannot be parsed as integers", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "odd-version", type: "rule", latestVersion: "abc", versionsCount: 1, updatedAt: "2026-02-14" },
      ];
      const assets = [
        { name: "odd-version", version: "xyz", type: "rule", clients: [], status: "installed", scope: "Global" },
      ];

      const result = mergeAssets(catalog, assets);

      expect(result[0].hasUpdate).toBe(false);
    });

    it("handles empty/null latestVersion gracefully", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "empty-ver", type: "rule", latestVersion: "", versionsCount: 0, updatedAt: "" },
      ];
      const assets: any[] = [];

      const result = mergeAssets(catalog, assets);

      expect(result[0].latestVersion).toBe("");
      expect(result[0].hasUpdate).toBe(false);
    });

    it("merges multiple catalog and asset entries correctly", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "rule-a", type: "rule", latestVersion: "3", versionsCount: 3, updatedAt: "2026-02-14" },
        { name: "skill-b", type: "skill", latestVersion: "2", versionsCount: 2, updatedAt: "2026-02-13" },
        { name: "cmd-c", type: "command", latestVersion: "1", versionsCount: 1, updatedAt: "2026-02-12" },
      ];
      const assets = [
        { name: "rule-a", version: "v3", type: "rule", clients: [], status: "installed", scope: "Global" },
        { name: "skill-b", version: "v1", type: "skill", clients: ["repo1"], status: "installed", scope: "repo1" },
      ];

      const result = mergeAssets(catalog, assets);

      expect(result).toHaveLength(3);

      const ruleA = result.find((a: any) => a.name === "rule-a")!;
      expect(ruleA.installed).toBe(true);
      expect(ruleA.hasUpdate).toBe(false);

      const skillB = result.find((a: any) => a.name === "skill-b")!;
      expect(skillB.installed).toBe(true);
      expect(skillB.hasUpdate).toBe(true);

      const cmdC = result.find((a: any) => a.name === "cmd-c")!;
      expect(cmdC.installed).toBe(false);
      expect(cmdC.hasUpdate).toBe(false);
    });

    it("strips 'v' prefix when comparing versions", async () => {
      const { mergeAssets } = await import("../../src/ui/viewer/hooks/useTeams.js");
      const catalog = [
        { name: "test", type: "rule", latestVersion: "3", versionsCount: 3, updatedAt: "" },
      ];
      const assets = [
        { name: "test", version: "v3", type: "rule", clients: [], status: "installed", scope: "Global" },
      ];

      const result = mergeAssets(catalog, assets);

      expect(result[0].hasUpdate).toBe(false);
    });
  });

  it("source contains API endpoint fetch logic", async () => {
    const fs = await import("fs");
    const source = fs.readFileSync("src/ui/viewer/hooks/useTeams.ts", "utf-8");

    expect(source).toContain("/api/teams/status");
    expect(source).toContain("/api/teams/detail/");
    expect(source).toContain("/api/teams/install");
    expect(source).toContain("isInstalling");
    expect(source).toContain("mergeAssets");
    expect(source).toContain("/api/teams/remove");
    expect(source).toContain("removeAsset");
    expect(source).toContain("/api/teams/init");
    expect(source).toContain("initTeams");
  });
});
