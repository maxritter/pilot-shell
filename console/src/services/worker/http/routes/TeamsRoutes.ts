/**
 * TeamsRoutes
 *
 * API endpoints for sx team asset status and management.
 * Invokes the sx CLI via Bun.spawn with timeout and caching.
 */

import path from "path";
import { readdirSync, existsSync } from "fs";
import express, { type Request, type Response } from "express";
import { BaseRouteHandler } from "../BaseRouteHandler.js";
import { logger } from "../../../../utils/logger.js";

export interface TeamsAsset {
  name: string;
  version: string;
  type: string;
  clients: string[];
  status: string;
  scope: string;
}

export interface TeamsCatalogItem {
  name: string;
  type: string;
  latestVersion: string;
  versionsCount: number;
  updatedAt: string;
}

export interface TeamsStatusResponse {
  installed: boolean;
  version: string | null;
  configured: boolean;
  repoUrl: string | null;
  profile: string | null;
  assets: TeamsAsset[];
  catalog: TeamsCatalogItem[];
  isInstalling: boolean;
}

interface TeamsDetailResponse {
  name: string;
  type: string;
  metadata: {
    description: string | null;
    authors: string[];
    keywords: string[];
  };
  versions: Array<{
    version: string;
    createdAt: string | null;
    filesCount: number;
  }>;
}

const NAME_REGEX = /^[a-zA-Z0-9-]+$/;
const STATUS_TIMEOUT_MS = 15_000;
const INSTALL_TIMEOUT_MS = 60_000;
const PUSH_TIMEOUT_MS = 30_000;
const INIT_TIMEOUT_MS = 30_000;
const REMOVE_TIMEOUT_MS = 15_000;

const STATUS_CACHE_TTL_MS = 30_000;
const DETAIL_CACHE_TTL_MS = 60_000;

export class TeamsRoutes extends BaseRouteHandler {
  private statusCache: { data: TeamsStatusResponse; timestamp: number } | null =
    null;
  private detailCache: Map<
    string,
    { data: TeamsDetailResponse; timestamp: number }
  > = new Map();
  private _isInstalling = false;

  setupRoutes(app: express.Application): void {
    app.get("/api/teams/status", this.handleStatus.bind(this));
    app.post("/api/teams/install", this.handleInstall.bind(this));
    app.get("/api/teams/detail/:name", this.handleDetail.bind(this));
    app.post("/api/teams/push", this.handlePush.bind(this));
    app.post("/api/teams/remove", this.handleRemove.bind(this));
    app.post("/api/teams/init", this.handleInit.bind(this));
    app.get("/api/teams/discover", this.handleDiscover.bind(this));
    app.post("/api/teams/update-asset", this.handleUpdateAsset.bind(this));
  }

  private handleStatus = this.wrapHandler(
    async (_req: Request, res: Response): Promise<void> => {
      if (
        this.statusCache &&
        Date.now() - this.statusCache.timestamp < STATUS_CACHE_TTL_MS
      ) {
        res.json({
          ...this.statusCache.data,
          isInstalling: this._isInstalling,
        });
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.json(this.emptyStatus());
        return;
      }

      try {
        const [configOutput, catalogOutput] = await Promise.all([
          this.runSxCommand([sxPath, "config", "--json"], STATUS_TIMEOUT_MS),
          this.runSxCommand(
            [sxPath, "vault", "list", "--json"],
            STATUS_TIMEOUT_MS,
          ).catch(() => "[]"),
        ]);

        const config = JSON.parse(configOutput);
        const catalog: TeamsCatalogItem[] = JSON.parse(catalogOutput).map(
          (item: any) => ({
            name: item.name,
            type: item.type,
            latestVersion: item.latestVersion,
            versionsCount: item.versionsCount,
            updatedAt: item.updatedAt,
          }),
        );

        const assets: TeamsAsset[] = [];
        for (const scopeGroup of config.assets || []) {
          const scope = scopeGroup.scope || "Global";
          for (const asset of scopeGroup.assets || []) {
            assets.push({
              name: asset.name,
              version: asset.version,
              type: asset.type,
              clients: asset.clients || [],
              status: asset.status || "unknown",
              scope,
            });
          }
        }

        const status: TeamsStatusResponse = {
          installed: true,
          version: config.version?.version || null,
          configured: !!config.config?.repositoryUrl,
          repoUrl: config.config?.repositoryUrl || null,
          profile: config.config?.profile || null,
          assets,
          catalog,
          isInstalling: this._isInstalling,
        };

        this.statusCache = { data: status, timestamp: Date.now() };
        res.json(status);
      } catch (error) {
        logger.error("HTTP", "Teams status failed", {}, error as Error);
        res.json(this.emptyStatus());
      }
    },
  );

  private handleInstall = this.wrapHandler(
    async (_req: Request, res: Response): Promise<void> => {
      if (this._isInstalling) {
        res.status(409).json({ error: "Installation already in progress" });
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }

      const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();

      this._isInstalling = true;
      this.statusCache = null;
      res.json({ started: true });

      try {
        await this.runSxCommand(
          [sxPath, "install", "--repair", "--target", projectRoot],
          INSTALL_TIMEOUT_MS,
        );
        logger.info("HTTP", "Teams install --repair completed");
      } catch (error) {
        logger.error("HTTP", "Teams install failed", {}, error as Error);
      } finally {
        this._isInstalling = false;
        this.statusCache = null;
        this.detailCache.clear();
      }
    },
  );

  private handleDetail = this.wrapHandler(
    async (req: Request, res: Response): Promise<void> => {
      const name = req.params.name;

      if (!name || !NAME_REGEX.test(name)) {
        res.status(400).json({
          error:
            "Invalid asset name: only alphanumeric characters and hyphens allowed",
        });
        return;
      }

      const cached = this.detailCache.get(name);
      if (cached && Date.now() - cached.timestamp < DETAIL_CACHE_TTL_MS) {
        res.json(cached.data);
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }

      try {
        const output = await this.runSxCommand(
          [sxPath, "vault", "show", name, "--json"],
          STATUS_TIMEOUT_MS,
        );
        const data = JSON.parse(output);

        if (!data.name || !data.type) {
          logger.error("HTTP", "Unexpected sx vault show output", {
            name,
            raw: output.slice(0, 500),
          });
          res.status(502).json({ error: "Unexpected sx response format" });
          return;
        }

        const detail = {
          name: data.name,
          type: data.type,
          metadata: {
            description: data.metadata?.description ?? null,
            authors: data.metadata?.authors ?? [],
            keywords: data.metadata?.keywords ?? [],
          },
          versions: (data.versions ?? []).map((v: any) => ({
            version: v.version,
            createdAt: v.createdAt ?? null,
            filesCount: v.filesCount ?? 0,
          })),
        };

        this.detailCache.set(name, { data: detail, timestamp: Date.now() });
        res.json(detail);
      } catch (error) {
        const message = (error as Error).message || "";
        if (message.includes("exited with code")) {
          res.status(404).json({ error: `Asset '${name}' not found` });
        } else {
          logger.error("HTTP", "Teams detail failed", { name }, error as Error);
          res.status(502).json({ error: "Unexpected sx response format" });
        }
      }
    },
  );

  private handlePush = this.wrapHandler(
    async (req: Request, res: Response): Promise<void> => {
      const { source, type, name, scope, scopeUrl } = req.body;

      if (!source || !type || !name) {
        res.status(400).json({ error: "source, type, and name are required" });
        return;
      }

      if (!NAME_REGEX.test(name)) {
        res.status(400).json({
          error:
            "Invalid asset name: only alphanumeric characters and hyphens allowed",
        });
        return;
      }

      const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
      const resolvedSource = path.resolve(projectRoot, source);
      if (
        resolvedSource !== projectRoot &&
        !resolvedSource.startsWith(projectRoot + path.sep)
      ) {
        res.status(400).json({ error: "Source path must be within project" });
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }

      const args = [
        sxPath,
        "add",
        resolvedSource,
        "--type",
        type,
        "--name",
        name,
        "--yes",
      ];

      if (scope === "global") {
        args.push("--scope-global");
      } else if (scopeUrl) {
        args.push("--scope-repo", scopeUrl);
      }

      try {
        await this.runSxCommand(args, PUSH_TIMEOUT_MS);
        this.statusCache = null;
        this.detailCache.clear();
        res.json({ success: true, error: null });
      } catch (error) {
        const message = (error as Error).message || "Push failed";
        logger.error("HTTP", "Teams push failed", { name }, error as Error);
        res.json({ success: false, error: message });
      }
    },
  );

  private handleRemove = this.wrapHandler(
    async (req: Request, res: Response): Promise<void> => {
      const { name } = req.body;

      if (!name || !NAME_REGEX.test(name)) {
        res.status(400).json({
          error:
            "Invalid asset name: only alphanumeric characters and hyphens allowed",
        });
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }

      try {
        await this.runSxCommand(
          [sxPath, "remove", name, "--yes"],
          REMOVE_TIMEOUT_MS,
        );
        this.statusCache = null;
        this.detailCache.clear();
        res.json({ success: true, error: null });
      } catch (error) {
        const message = (error as Error).message || "Remove failed";
        logger.error("HTTP", "Teams remove failed", { name }, error as Error);
        res.json({ success: false, error: message });
      }
    },
  );

  private handleInit = this.wrapHandler(
    async (req: Request, res: Response): Promise<void> => {
      const { type, repoUrl } = req.body;

      if (!type || !repoUrl) {
        res.status(400).json({ error: "type and repoUrl are required" });
        return;
      }

      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }

      try {
        await this.runSxCommand(
          [
            sxPath,
            "init",
            "--type",
            type,
            "--repo-url",
            repoUrl,
            "--clients",
            "claude-code",
          ],
          INIT_TIMEOUT_MS,
        );
        this.statusCache = null;
        res.json({ success: true, error: null });
      } catch (error) {
        const message = (error as Error).message || "Init failed";
        logger.error("HTTP", "Teams init failed", {}, error as Error);
        res.json({ success: false, error: message });
      }
    },
  );

  private handleDiscover = this.wrapHandler(
    async (_req: Request, res: Response): Promise<void> => {
      const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
      const claudeDir = path.join(projectRoot, ".claude");

      const discovered: { name: string; type: string; path: string }[] = [];

      const typeMap: Record<string, string> = {
        skills: "skill",
        rules: "rule",
        commands: "command",
      };

      for (const [dir, type] of Object.entries(typeMap)) {
        const fullPath = path.join(claudeDir, dir);
        if (!existsSync(fullPath)) continue;

        try {
          const entries = readdirSync(fullPath, { withFileTypes: true });
          for (const entry of entries) {
            const assetName = entry.isDirectory()
              ? entry.name
              : entry.name.replace(/\.md$/, "");
            if (!assetName || assetName.startsWith(".")) continue;
            discovered.push({
              name: assetName,
              type,
              path: path.join(".claude", dir, entry.name),
            });
          }
        } catch {
          // Directory not readable
        }
      }

      // Get repo URL
      let repoUrl: string | null = null;
      try {
        const proc = Bun.spawn(["git", "remote", "get-url", "origin"], {
          cwd: projectRoot,
          stdout: "pipe",
          stderr: "pipe",
        });
        const stdout = await new Response(proc.stdout).text();
        const exitCode = await proc.exited;
        if (exitCode === 0 && stdout.trim()) {
          repoUrl = stdout.trim();
        }
      } catch {
        // Not a git repo or git not available
      }

      res.json({ assets: discovered, repoUrl });
    },
  );

  private handleUpdateAsset = this.wrapHandler(
    async (req: Request, res: Response): Promise<void> => {
      const { name, currentVersion, scope, scopeUrl } = req.body;
      if (!name || !NAME_REGEX.test(name)) {
        res.status(400).json({ error: "Invalid asset name" });
        return;
      }
      const sxPath = this.resolveSxBinary();
      if (!sxPath) {
        res.status(500).json({ error: "sx CLI not found" });
        return;
      }
      try {
        // Remove old version from lock file
        if (currentVersion) {
          await this.runSxCommand(
            [
              sxPath,
              "remove",
              name,
              "--version",
              String(currentVersion),
              "--yes",
            ],
            REMOVE_TIMEOUT_MS,
          );
        }
        // Re-add with scope (picks up latest version)
        const addArgs = [sxPath, "add", name, "--yes"];
        if (scope === "global") {
          addArgs.push("--scope-global");
        } else if (scopeUrl) {
          addArgs.push("--scope-repo", scopeUrl);
        } else {
          addArgs.push("--scope-global");
        }
        await this.runSxCommand(addArgs, PUSH_TIMEOUT_MS);
        // Install the updated version
        const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
        await this.runSxCommand(
          [sxPath, "install", "--repair", "--target", projectRoot],
          INSTALL_TIMEOUT_MS,
        );
        this.statusCache = null;
        this.detailCache.clear();
        res.json({ success: true, error: null });
      } catch (error) {
        const message = (error as Error).message || "Update failed";
        logger.error(
          "HTTP",
          "Teams update-asset failed",
          { name },
          error as Error,
        );
        res.json({ success: false, error: message });
      }
    },
  );

  private emptyStatus(): TeamsStatusResponse {
    return {
      installed: false,
      version: null,
      configured: false,
      repoUrl: null,
      profile: null,
      assets: [],
      catalog: [],
      isInstalling: this._isInstalling,
    };
  }

  private resolveSxBinary(): string | null {
    const found = Bun.which("sx");
    return found || null;
  }

  private async runSxCommand(
    args: string[],
    timeoutMs: number,
  ): Promise<string> {
    const proc = Bun.spawn(args, {
      stdout: "pipe",
      stderr: "pipe",
    });

    const timeoutId = setTimeout(() => {
      try {
        proc.kill("SIGTERM");
        setTimeout(() => {
          try {
            proc.kill("SIGKILL");
          } catch {}
        }, 1000);
      } catch {}
    }, timeoutMs);

    try {
      const [stdout, stderr] = await Promise.all([
        new Response(proc.stdout).text(),
        new Response(proc.stderr).text(),
      ]);
      const exitCode = await proc.exited;

      if (exitCode !== 0) {
        throw new Error(
          `sx exited with code ${exitCode}: ${stderr.slice(0, 200)}`,
        );
      }

      return stdout;
    } finally {
      clearTimeout(timeoutId);
    }
  }
}
