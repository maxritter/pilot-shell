/**
 * Git repository info utility.
 * Reads branch and status from a project root directory.
 */

import { execSync } from "child_process";

export interface GitInfo {
  branch: string | null;
  staged: number;
  unstaged: number;
  untracked: number;
}

export function getGitInfo(projectRoot: string): GitInfo {
  try {
    const branch = execSync("git rev-parse --abbrev-ref HEAD", {
      cwd: projectRoot,
      encoding: "utf-8",
      timeout: 2000,
    }).trim();

    const status = execSync("git status --porcelain", {
      cwd: projectRoot,
      encoding: "utf-8",
      timeout: 2000,
    });

    let staged = 0;
    let unstaged = 0;
    let untracked = 0;

    for (const line of status.split("\n")) {
      if (!line) continue;
      const idx = line[0] || " ";
      const wt = line[1] || " ";

      if (idx === "?" && wt === "?") {
        untracked++;
      } else {
        if (idx !== " " && idx !== "?") staged++;
        if (wt !== " ") unstaged++;
      }
    }

    return { branch, staged, unstaged, untracked };
  } catch {
    return { branch: null, staged: 0, unstaged: 0, untracked: 0 };
  }
}
