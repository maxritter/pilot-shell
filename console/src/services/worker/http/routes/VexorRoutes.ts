/**
 * VexorRoutes
 *
 * API endpoints for Vexor semantic search status and codebase search.
 * Invokes the Vexor CLI via Bun.spawn with timeout and concurrency controls.
 */

import express, { type Request, type Response } from "express";
import { BaseRouteHandler } from "../BaseRouteHandler.js";
import { logger } from "../../../../utils/logger.js";
import type { DatabaseManager } from "../../DatabaseManager.js";
import { resolveProjectRoot } from "./utils/resolveProjectRoot.js";
import type { Subprocess } from "bun";

export interface VexorStatus {
  isIndexed: boolean;
  files: number;
  mode: string;
  model: string;
  generatedAt: string | null;
  embeddingDim: number;
  version: number;
}

export interface VexorSearchResult {
  rank: number;
  score: number;
  filePath: string;
  chunkIndex: number;
  startLine: number | null;
  endLine: number | null;
  snippet: string;
}

const MAX_CONCURRENT_PROCESSES = 3;
const SEARCH_TIMEOUT_MS = 120_000;
const REINDEX_TIMEOUT_MS = 600_000;
const STATUS_TIMEOUT_MS = 30_000;
const STATUS_CACHE_TTL_MS = 60_000;

/**
 * Parse `vexor index --show` human-readable output into structured data.
 */
export function parseVexorIndexOutput(output: string): VexorStatus {
  const defaults: VexorStatus = {
    isIndexed: false,
    files: 0,
    mode: "",
    model: "",
    generatedAt: null,
    embeddingDim: 0,
    version: 0,
  };

  if (!output || !output.includes("Files:")) {
    return defaults;
  }

  const getValue = (key: string): string => {
    const match = output.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
    return match ? match[1].trim() : "";
  };

  const files = parseInt(getValue("Files"), 10) || 0;

  return {
    isIndexed: files > 0,
    files,
    mode: getValue("Mode"),
    model: getValue("Model"),
    generatedAt: getValue("Generated at") || null,
    embeddingDim: parseInt(getValue("Embedding dimension"), 10) || 0,
    version: parseInt(getValue("Version"), 10) || 0,
  };
}

/**
 * Parse `vexor search --format porcelain` TSV output into structured results.
 * Format: rank\tscore\tpath\tchunk_index\tstart_line\tend_line\tsnippet
 */
export function parseVexorSearchOutput(output: string): VexorSearchResult[] {
  if (!output.trim()) {
    return [];
  }

  const results: VexorSearchResult[] = [];

  for (const line of output.trim().split("\n")) {
    const parts = line.split("\t");
    if (parts.length < 7) continue;

    const rank = parseInt(parts[0], 10);
    const score = parseFloat(parts[1]);
    if (isNaN(rank) || isNaN(score)) continue;

    results.push({
      rank,
      score,
      filePath: parts[2],
      chunkIndex: parseInt(parts[3], 10) || 0,
      startLine: parts[4] === "-" ? null : parseInt(parts[4], 10) || null,
      endLine: parts[5] === "-" ? null : parseInt(parts[5], 10) || null,
      snippet: parts.slice(6).join("\t"),
    });
  }

  return results;
}

export class VexorRoutes extends BaseRouteHandler {
  private dbManager: DatabaseManager | null;
  private activeProcesses = new Set<Subprocess>();
  private statusCache = new Map<string, { data: VexorStatus; timestamp: number }>();
  private _isReindexing = false;

  constructor(dbManager?: DatabaseManager) {
    super();
    this.dbManager = dbManager ?? null;
  }

  setupRoutes(app: express.Application): void {
    app.get("/api/vexor/status", this.handleStatus.bind(this));
    app.get("/api/vexor/search", this.handleSearch.bind(this));
    app.post("/api/vexor/reindex", this.handleReindex.bind(this));
  }

  /** Kill all tracked active Vexor processes. Call during worker shutdown. */
  dispose(): void {
    for (const proc of this.activeProcesses) {
      try {
        proc.kill();
      } catch {}
    }
    this.activeProcesses.clear();
    logger.debug("HTTP", "VexorRoutes disposed, killed active processes");
  }

  private handleStatus = this.wrapHandler(async (req: Request, res: Response): Promise<void> => {
    const project = req.query.project as string | undefined;
    const projectRoot = resolveProjectRoot(this.dbManager, project);
    const cached = this.statusCache.get(projectRoot);
    if (cached && Date.now() - cached.timestamp < STATUS_CACHE_TTL_MS) {
      res.json({ ...cached.data, isReindexing: this._isReindexing });
      return;
    }

    const vexorPath = this.resolveVexorBinary();
    if (!vexorPath) {
      res.json(this.emptyStatus());
      return;
    }

    try {
      const output = await this.runVexorCommand(
        [vexorPath, "index", "--show", "--path", projectRoot],
        STATUS_TIMEOUT_MS,
      );
      const status = parseVexorIndexOutput(output);
      this.statusCache.set(projectRoot, { data: status, timestamp: Date.now() });
      res.json({ ...status, isReindexing: this._isReindexing });
    } catch (error) {
      logger.error("HTTP", "Vexor status failed", {}, error as Error);
      res.json(this.emptyStatus());
    }
  });

  private handleSearch = this.wrapHandler(async (req: Request, res: Response): Promise<void> => {
    const query = req.query.query as string;
    if (!query) {
      this.badRequest(res, "query parameter is required");
      return;
    }

    if (this.activeProcesses.size >= MAX_CONCURRENT_PROCESSES) {
      res.status(429).json({ error: "Too many concurrent searches. Try again shortly." });
      return;
    }

    const vexorPath = this.resolveVexorBinary();
    if (!vexorPath) {
      res.json({ results: [], error: "Vexor CLI not found" });
      return;
    }

    const project = req.query.project as string | undefined;
    const projectRoot = resolveProjectRoot(this.dbManager, project);
    const top = parseInt(req.query.top as string, 10) || 20;
    const mode = (req.query.mode as string) || "auto";

    const args = [
      vexorPath, "search", query,
      "--top", String(top),
      "--mode", mode,
      "--format", "porcelain",
      "--path", projectRoot,
    ];

    const ext = req.query.ext as string;
    if (ext) {
      args.push("--ext", ext);
    }

    try {
      const output = await this.runVexorCommand(args, SEARCH_TIMEOUT_MS);
      const results = parseVexorSearchOutput(output);
      res.json({ results, query });
    } catch (error) {
      logger.error("HTTP", "Vexor search failed", { query }, error as Error);
      res.status(500).json({ error: (error as Error).message });
    }
  });

  private handleReindex = this.wrapHandler(async (req: Request, res: Response): Promise<void> => {
    if (this._isReindexing) {
      res.status(409).json({ error: "Reindexing already in progress" });
      return;
    }

    const vexorPath = this.resolveVexorBinary();
    if (!vexorPath) {
      res.status(500).json({ error: "Vexor CLI not found" });
      return;
    }

    const project = req.query.project as string | undefined;
    const projectRoot = resolveProjectRoot(this.dbManager, project);
    this._isReindexing = true;
    this.statusCache.clear();

    res.json({ started: true });

    try {
      await this.runVexorCommand(
        [vexorPath, "index", "--clear", "--path", projectRoot],
        REINDEX_TIMEOUT_MS,
      );
      await this.runVexorCommand(
        [vexorPath, "index", "--path", projectRoot],
        REINDEX_TIMEOUT_MS,
      );
      logger.info("HTTP", "Vexor reindex completed");
    } catch (error) {
      logger.error("HTTP", "Vexor reindex failed", {}, error as Error);
    } finally {
      this._isReindexing = false;
      this.statusCache.clear();
    }
  });

  private emptyStatus(): VexorStatus & { isReindexing: boolean } {
    return {
      isIndexed: false,
      files: 0,
      mode: "",
      model: "",
      generatedAt: null,
      embeddingDim: 0,
      version: 0,
      isReindexing: this._isReindexing,
    };
  }

  private resolveVexorBinary(): string | null {
    if (process.env.VEXOR_PATH) {
      return process.env.VEXOR_PATH;
    }

    const found = Bun.which("vexor");
    return found || null;
  }

  private async runVexorCommand(args: string[], timeoutMs: number): Promise<string> {
    const proc = Bun.spawn(args, {
      stdout: "pipe",
      stderr: "pipe",
    });

    this.activeProcesses.add(proc);

    const timeoutId = setTimeout(() => {
      try {
        proc.kill();
      } catch {}
    }, timeoutMs);

    try {
      const [stdout, stderr] = await Promise.all([
        new Response(proc.stdout).text(),
        new Response(proc.stderr).text(),
      ]);
      const exitCode = await proc.exited;

      if (exitCode !== 0) {
        throw new Error(`Vexor exited with code ${exitCode}: ${stderr.slice(0, 200)}`);
      }

      return stdout;
    } finally {
      clearTimeout(timeoutId);
      this.activeProcesses.delete(proc);
    }
  }
}
