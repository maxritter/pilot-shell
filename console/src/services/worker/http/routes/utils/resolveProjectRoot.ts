/**
 * Resolve project root path from a project name via the project_roots table.
 * Falls back to CLAUDE_PROJECT_ROOT env var or cwd() when project is not specified
 * or not found in the database.
 */

import { existsSync, statSync } from "fs";
import type { DatabaseManager } from "../../../DatabaseManager.js";

export function resolveProjectRoot(
  dbManager: DatabaseManager | null,
  project?: string,
): string {
  const defaultRoot = process.env.CLAUDE_PROJECT_ROOT || process.cwd();

  if (!project) {
    return defaultRoot;
  }

  if (!dbManager) {
    return defaultRoot;
  }

  const root = dbManager.getSessionStore().getProjectRoot(project);
  if (!root) {
    return defaultRoot;
  }

  if (!existsSync(root) || !statSync(root).isDirectory()) {
    return defaultRoot;
  }

  return root;
}
