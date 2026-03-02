/**
 * TeamsView Component Tests
 *
 * Tests for the Teams page components: TeamsView, TeamsSummaryCards,
 * TeamsAssetTable, and TeamsAssetDetail.
 */

import { describe, it, expect } from "bun:test";
import { renderToString } from "react-dom/server";
import React from "react";

describe("TeamsView", () => {
  it("TeamsView is exported from views/Teams", async () => {
    const mod = await import("../../src/ui/viewer/views/Teams/index.js");
    expect(mod.TeamsView).toBeDefined();
    expect(typeof mod.TeamsView).toBe("function");
  });

  it("TeamsSummaryCards is exported", async () => {
    const mod = await import("../../src/ui/viewer/views/Teams/TeamsSummaryCards.js");
    expect(mod.TeamsSummaryCards).toBeDefined();
    expect(typeof mod.TeamsSummaryCards).toBe("function");
  });

  it("TeamsAssetTable is exported", async () => {
    const mod = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");
    expect(mod.TeamsAssetTable).toBeDefined();
    expect(typeof mod.TeamsAssetTable).toBe("function");
  });

  it("TeamsAssetDetail is exported", async () => {
    const mod = await import("../../src/ui/viewer/views/Teams/TeamsAssetDetail.js");
    expect(mod.TeamsAssetDetail).toBeDefined();
    expect(typeof mod.TeamsAssetDetail).toBe("function");
  });

  describe("TeamsSummaryCards", () => {
    it("renders summary stats for assets", async () => {
      const { TeamsSummaryCards } = await import("../../src/ui/viewer/views/Teams/TeamsSummaryCards.js");

      const assets = [
        { name: "a", type: "skill", latestVersion: "1", versionsCount: 1, installedVersion: "v1", installed: true, hasUpdate: false, scope: null, clients: [] },
        { name: "b", type: "rule", latestVersion: "2", versionsCount: 2, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
        { name: "c", type: "command", latestVersion: "1", versionsCount: 1, installedVersion: "v1", installed: true, hasUpdate: true, scope: null, clients: [] },
        { name: "d", type: "skill", latestVersion: "3", versionsCount: 3, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
      ];

      const html = renderToString(React.createElement(TeamsSummaryCards, { assets }));

      expect(html).toContain("4");
      expect(html).toContain("Skills");
      expect(html).toContain("Rules");
    });
  });

  describe("TeamsAssetTable", () => {
    it("renders asset rows", async () => {
      const { TeamsAssetTable } = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");

      const assets = [
        { name: "my-skill", type: "skill", latestVersion: "3", versionsCount: 3, installedVersion: "v2", installed: true, hasUpdate: true, scope: "Global", clients: [] },
        { name: "my-rule", type: "rule", latestVersion: "1", versionsCount: 1, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
      ];

      const html = renderToString(
        React.createElement(TeamsAssetTable, {
          assets,
          searchQuery: "",
          activeTab: "all",
          onTabChange: () => {},
          onSearchChange: () => {},
          expandedAsset: null,
          onAssetClick: () => {},
          fetchDetail: () => Promise.resolve(),
          detailCache: new Map(),
          loadingDetails: new Set<string>(),
          tier: "team",
          onUpdate: () => {},
          onRemove: () => Promise.resolve(),
        }),
      );

      expect(html).toContain("my-skill");
      expect(html).toContain("my-rule");
    });

    it("renders action buttons for installed assets with update", async () => {
      const { TeamsAssetTable } = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");

      const assets = [
        { name: "my-skill", type: "skill", latestVersion: "3", versionsCount: 3, installedVersion: "v2", installed: true, hasUpdate: true, scope: "Global", clients: [] },
      ];

      const html = renderToString(
        React.createElement(TeamsAssetTable, {
          assets,
          searchQuery: "",
          activeTab: "all",
          onTabChange: () => {},
          onSearchChange: () => {},
          expandedAsset: null,
          onAssetClick: () => {},
          fetchDetail: () => Promise.resolve(),
          detailCache: new Map(),
          loadingDetails: new Set<string>(),
          tier: "team",
          onUpdate: () => {},
          onRemove: () => Promise.resolve(),
        }),
      );

      expect(html).toContain("Update");
      expect(html).toContain("Remove");
    });

    it("renders install button for uninstalled vault assets", async () => {
      const { TeamsAssetTable } = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");

      const assets = [
        { name: "my-rule", type: "rule", latestVersion: "1", versionsCount: 1, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
      ];

      const html = renderToString(
        React.createElement(TeamsAssetTable, {
          assets,
          searchQuery: "",
          activeTab: "all",
          onTabChange: () => {},
          onSearchChange: () => {},
          expandedAsset: null,
          onAssetClick: () => {},
          fetchDetail: () => Promise.resolve(),
          detailCache: new Map(),
          loadingDetails: new Set<string>(),
          tier: "solo",
          onUpdate: () => {},
          onRemove: () => Promise.resolve(),
        }),
      );

      expect(html).toContain("Install");
      expect(html).not.toContain("Remove");
    });

    it("filters by search query", async () => {
      const { TeamsAssetTable } = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");

      const assets = [
        { name: "my-skill", type: "skill", latestVersion: "3", versionsCount: 3, installedVersion: "v2", installed: true, hasUpdate: true, scope: "Global", clients: [] },
        { name: "my-rule", type: "rule", latestVersion: "1", versionsCount: 1, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
      ];

      const html = renderToString(
        React.createElement(TeamsAssetTable, {
          assets,
          searchQuery: "skill",
          activeTab: "all",
          onTabChange: () => {},
          onSearchChange: () => {},
          expandedAsset: null,
          onAssetClick: () => {},
          fetchDetail: () => Promise.resolve(),
          detailCache: new Map(),
          loadingDetails: new Set<string>(),
          tier: null,
          onUpdate: () => {},
          onRemove: () => Promise.resolve(),
        }),
      );

      expect(html).toContain("my-skill");
      expect(html).not.toContain("my-rule");
    });

    it("filters by tab type", async () => {
      const { TeamsAssetTable } = await import("../../src/ui/viewer/views/Teams/TeamsAssetTable.js");

      const assets = [
        { name: "my-skill", type: "skill", latestVersion: "3", versionsCount: 3, installedVersion: "v2", installed: true, hasUpdate: true, scope: "Global", clients: [] },
        { name: "my-rule", type: "rule", latestVersion: "1", versionsCount: 1, installedVersion: null, installed: false, hasUpdate: false, scope: null, clients: [] },
      ];

      const html = renderToString(
        React.createElement(TeamsAssetTable, {
          assets,
          searchQuery: "",
          activeTab: "rule",
          onTabChange: () => {},
          onSearchChange: () => {},
          expandedAsset: null,
          onAssetClick: () => {},
          fetchDetail: () => Promise.resolve(),
          detailCache: new Map(),
          loadingDetails: new Set<string>(),
          tier: null,
          onUpdate: () => {},
          onRemove: () => Promise.resolve(),
        }),
      );

      expect(html).toContain("my-rule");
      expect(html).not.toContain("my-skill");
    });
  });

  describe("TeamsAssetDetail", () => {
    it("renders version history when detail is loaded", async () => {
      const { TeamsAssetDetail } = await import("../../src/ui/viewer/views/Teams/TeamsAssetDetail.js");

      const detail = {
        name: "lsp-cleaner",
        type: "skill",
        metadata: { description: "Clean up unused code", authors: ["test"], keywords: [] },
        versions: [
          { version: "3", createdAt: "2026-02-14", filesCount: 5 },
          { version: "2", createdAt: "2026-02-10", filesCount: 4 },
        ],
      };

      const html = renderToString(
        React.createElement(TeamsAssetDetail, {
          detail,
          isLoading: false,
        }),
      );

      expect(html).toContain("Clean up unused code");
      expect(html).toContain("5");
    });

    it("renders loading spinner when fetching", async () => {
      const { TeamsAssetDetail } = await import("../../src/ui/viewer/views/Teams/TeamsAssetDetail.js");

      const html = renderToString(
        React.createElement(TeamsAssetDetail, {
          detail: null,
          isLoading: true,
        }),
      );

      expect(html).toContain("loading");
    });
  });
});

describe("TeamsSetupTab", () => {
  it("renders Reconfigure button when configured", async () => {
    const { TeamsSetupTab } = await import("../../src/ui/viewer/views/Teams/TeamsSetupTab.js");

    const configuredStatus = {
      installed: true, version: "0.12.4", configured: true,
      repoUrl: "git@github.com:org/team-vault.git", profile: "default",
      assets: [], catalog: [], isInstalling: false,
    };

    const html = renderToString(
      React.createElement(TeamsSetupTab, {
        teamsStatus: configuredStatus as any,
        initTeams: () => Promise.resolve({ success: true, error: null }),
      }),
    );

    expect(html).toContain("Reconfigure");
    expect(html).toContain("Repository Configuration");
    expect(html).toContain("git@github.com:org/team-vault.git");
  });

  it("renders init form when not configured", async () => {
    const { TeamsSetupTab } = await import("../../src/ui/viewer/views/Teams/TeamsSetupTab.js");

    const unconfiguredStatus = {
      installed: true, version: "0.12.4", configured: false,
      repoUrl: null, profile: null, assets: [], catalog: [], isInstalling: false,
    };

    const html = renderToString(
      React.createElement(TeamsSetupTab, {
        teamsStatus: unconfiguredStatus as any,
        initTeams: () => Promise.resolve({ success: true, error: null }),
      }),
    );

    expect(html).toContain("Initialize Repository");
    expect(html).not.toContain("Reconfigure");
  });
});

describe("TeamGate", () => {
  it("renders children for team tier", async () => {
    const { TeamGate } = await import("../../src/ui/viewer/components/TeamGate.js");
    const html = renderToString(
      React.createElement(TeamGate, { tier: "team", featureName: "Test feature" },
        React.createElement("div", null, "Child content")
      )
    );
    expect(html).toContain("Child content");
    expect(html).not.toContain("Team Plan Required");
  });

  it("renders upgrade overlay for solo tier", async () => {
    const { TeamGate } = await import("../../src/ui/viewer/components/TeamGate.js");
    const html = renderToString(
      React.createElement(TeamGate, { tier: "solo", featureName: "Push assets" },
        React.createElement("div", null, "Locked content")
      )
    );
    expect(html).toContain("Team Plan Required");
    expect(html).toContain("Upgrade to Team");
    expect(html).toContain("https://pilot-shell.com/#pricing");
  });

  it("renders upgrade overlay for trial tier", async () => {
    const { TeamGate } = await import("../../src/ui/viewer/components/TeamGate.js");
    const html = renderToString(
      React.createElement(TeamGate, { tier: "trial", featureName: "Push assets" },
        React.createElement("div", null, "Locked content")
      )
    );
    expect(html).toContain("Team Plan Required");
  });

  it("renders upgrade overlay for null tier (expired/no license)", async () => {
    const { TeamGate } = await import("../../src/ui/viewer/components/TeamGate.js");
    const html = renderToString(
      React.createElement(TeamGate, { tier: null, featureName: "Push assets" },
        React.createElement("div", null, "Locked content")
      )
    );
    expect(html).toContain("Team Plan Required");
    expect(html).toContain("Upgrade to Team");
    // children still in DOM but visually blurred via CSS (pointer-events-none blur)
  });

  it("TeamGate is exported from components", async () => {
    const mod = await import("../../src/ui/viewer/components/TeamGate.js");
    expect(mod.TeamGate).toBeDefined();
    expect(typeof mod.TeamGate).toBe("function");
  });
});
