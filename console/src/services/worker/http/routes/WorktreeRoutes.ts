/**
 * Worktree Routes
 *
 * Provides worktree status and diff data for the Spec viewer.
 * Reads worktree state from session data and runs git commands.
 */

import express, { Request, Response } from "express";
import { execFileSync } from "child_process";
import { existsSync, readFileSync } from "fs";
import path from "path";
import { BaseRouteHandler } from "../BaseRouteHandler.js";

export interface WorktreeStatus {
  active: boolean;
  worktreePath: string | null;
  branch: string | null;
  baseBranch: string | null;
  planSlug: string | null;
}

export interface WorktreeFileChange {
  path: string;
  status: string;
  additions: number;
  deletions: number;
}

export class WorktreeRoutes extends BaseRouteHandler {
  setupRoutes(app: express.Application): void {
    app.get("/api/worktree/status", this.handleGetStatus.bind(this));
    app.get("/api/worktree/diff", this.handleGetDiff.bind(this));
    app.get("/api/worktree/diff/:file(*)", this.handleGetFileDiff.bind(this));
    app.post("/api/worktree/sync", this.handleSync.bind(this));
    app.post("/api/worktree/discard", this.handleDiscard.bind(this));
  }

  /** Get active worktree status. */
  private handleGetStatus = this.wrapHandler((_req: Request, res: Response): void => {
    const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
    const status = this.getWorktreeStatus(projectRoot);
    res.json(status);
  });

  /** Get list of changed files between worktree branch and base branch. */
  private handleGetDiff = this.wrapHandler((_req: Request, res: Response): void => {
    const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
    const status = this.getWorktreeStatus(projectRoot);

    if (!status.active || !status.branch || !status.baseBranch) {
      res.json({ active: false, files: [] });
      return;
    }

    const files = this.getChangedFiles(projectRoot, status.baseBranch, status.branch);
    res.json({ active: true, files });
  });

  /** Get diff content for a specific file. */
  private handleGetFileDiff = this.wrapHandler((req: Request, res: Response): void => {
    const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
    const status = this.getWorktreeStatus(projectRoot);
    const filePath = req.params.file;

    if (!status.active || !status.branch || !status.baseBranch) {
      this.badRequest(res, "No active worktree");
      return;
    }

    if (!filePath) {
      this.badRequest(res, "Missing file path");
      return;
    }

    try {
      const diff = execFileSync(
        "git", ["diff", `${status.baseBranch}...${status.branch}`, "--", filePath],
        { cwd: projectRoot, encoding: "utf-8", timeout: 5000 },
      );
      res.json({ file: filePath, diff });
    } catch {
      this.notFound(res, "File not found in diff");
    }
  });

  /** Sync worktree changes to base branch via squash merge. */
  private handleSync = this.wrapHandler((_req: Request, res: Response): void => {
    const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
    const status = this.getWorktreeStatus(projectRoot);

    if (!status.active || !status.branch || !status.baseBranch) {
      this.badRequest(res, "No active worktree");
      return;
    }

    try {
      const mainRoot = this.getMainRepoRoot(projectRoot);
      if (!mainRoot) {
        res.status(500).json({ error: "Cannot determine main repository root" });
        return;
      }

      execFileSync("git", ["checkout", status.baseBranch], { cwd: mainRoot, encoding: "utf-8", timeout: 10000 });
      execFileSync("git", ["merge", "--squash", status.branch], { cwd: mainRoot, encoding: "utf-8", timeout: 30000 });

      const slug = status.planSlug || status.branch.replace("spec/", "");
      execFileSync("git", ["commit", "-m", `feat: implement spec/${slug}`], { cwd: mainRoot, encoding: "utf-8", timeout: 10000 });

      const commitHash = execFileSync("git", ["rev-parse", "HEAD"], { cwd: mainRoot, encoding: "utf-8", timeout: 5000 }).toString().trim();

      const statOutput = execFileSync("git", ["diff", "--stat", "HEAD~1"], { cwd: mainRoot, encoding: "utf-8", timeout: 5000 }).toString();
      const filesChanged = this.countFilesFromStat(statOutput);

      execFileSync("git", ["worktree", "remove", projectRoot, "--force"], { cwd: mainRoot, encoding: "utf-8", timeout: 10000 });
      execFileSync("git", ["branch", "-D", status.branch], { cwd: mainRoot, encoding: "utf-8", timeout: 5000 });

      res.json({ success: true, files_changed: filesChanged, commit_hash: commitHash });
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  });

  /** Discard worktree without merging. */
  private handleDiscard = this.wrapHandler((_req: Request, res: Response): void => {
    const projectRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();
    const status = this.getWorktreeStatus(projectRoot);

    if (!status.active || !status.branch) {
      this.badRequest(res, "No active worktree");
      return;
    }

    try {
      const mainRoot = this.getMainRepoRoot(projectRoot);
      if (!mainRoot) {
        res.status(500).json({ error: "Cannot determine main repository root" });
        return;
      }

      execFileSync("git", ["worktree", "remove", projectRoot, "--force"], { cwd: mainRoot, encoding: "utf-8", timeout: 10000 });
      execFileSync("git", ["branch", "-D", status.branch], { cwd: mainRoot, encoding: "utf-8", timeout: 5000 });

      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: (error as Error).message });
    }
  });

  /** Get worktree status by checking git worktree list output. */
  private getWorktreeStatus(projectRoot: string): WorktreeStatus {
    try {
      const branch = execFileSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], {
        cwd: projectRoot,
        encoding: "utf-8",
        timeout: 2000,
      }).toString().trim();

      if (!branch.startsWith("spec/")) {
        return { active: false, worktreePath: null, branch: null, baseBranch: null, planSlug: null };
      }

      const mainRoot = this.getMainRepoRoot(projectRoot);
      let baseBranch = "main";

      if (mainRoot) {
        try {
          const wtList = execFileSync("git", ["worktree", "list"], {
            cwd: mainRoot,
            encoding: "utf-8",
            timeout: 2000,
          }).toString();
          const firstLine = wtList.split("\n")[0];
          const branchMatch = firstLine.match(/\[([^\]]+)\]/);
          if (branchMatch) {
            baseBranch = branchMatch[1];
          }
        } catch {
        }
      }

      const planSlug = branch.replace("spec/", "");

      return {
        active: true,
        worktreePath: projectRoot,
        branch,
        baseBranch,
        planSlug,
      };
    } catch {
      return { active: false, worktreePath: null, branch: null, baseBranch: null, planSlug: null };
    }
  }

  /** Get changed files between two branches. */
  private getChangedFiles(projectRoot: string, baseBranch: string, branch: string): WorktreeFileChange[] {
    try {
      const nameStatus = execFileSync(
        "git", ["diff", "--name-status", `${baseBranch}...${branch}`],
        { cwd: projectRoot, encoding: "utf-8", timeout: 10000 },
      ).toString();

      const numstat = execFileSync(
        "git", ["diff", "--numstat", `${baseBranch}...${branch}`],
        { cwd: projectRoot, encoding: "utf-8", timeout: 10000 },
      ).toString();

      return this.parseChangedFiles(nameStatus, numstat);
    } catch {
      return [];
    }
  }

  /** Parse git diff --name-status and --numstat output into file change list. */
  parseChangedFiles(nameStatus: string, numstat: string): WorktreeFileChange[] {
    const statsByPath = new Map<string, { additions: number; deletions: number }>();
    for (const line of numstat.split("\n")) {
      if (!line.trim()) continue;
      const parts = line.split("\t");
      if (parts.length >= 3) {
        statsByPath.set(parts[2], {
          additions: parseInt(parts[0], 10) || 0,
          deletions: parseInt(parts[1], 10) || 0,
        });
      }
    }

    const files: WorktreeFileChange[] = [];
    for (const line of nameStatus.split("\n")) {
      if (!line.trim()) continue;
      const parts = line.split("\t");
      if (parts.length >= 2) {
        const status = parts[0].charAt(0);
        const filePath = parts[parts.length - 1];
        const stats = statsByPath.get(filePath) || { additions: 0, deletions: 0 };
        files.push({ path: filePath, status, additions: stats.additions, deletions: stats.deletions });
      }
    }
    return files;
  }

  /** Get the main repository root (for worktrees, this is the parent repo). */
  private getMainRepoRoot(projectRoot: string): string | null {
    try {
      const gitPath = path.join(projectRoot, ".git");
      if (existsSync(gitPath)) {
        try {
          const content = readFileSync(gitPath, "utf-8").trim();
          if (content.startsWith("gitdir:")) {
            const gitdir = content.replace("gitdir:", "").trim();
            const mainGitDir = path.resolve(projectRoot, gitdir, "..", "..");
            return path.dirname(mainGitDir);
          }
        } catch {
          return projectRoot;
        }
      }
      return projectRoot;
    } catch {
      return null;
    }
  }

  /** Count files changed from git diff --stat output. */
  private countFilesFromStat(statOutput: string): number {
    const lines = statOutput.trim().split("\n");
    if (lines.length === 0) return 0;
    const lastLine = lines[lines.length - 1];
    const match = lastLine.match(/(\d+) files? changed/);
    return match ? parseInt(match[1], 10) : 0;
  }
}
