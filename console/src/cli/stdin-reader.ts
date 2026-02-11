import { statSync } from "fs";

/**
 * Check if stdin is valid and readable.
 * Bun can crash when trying to read from an invalid stdin fd.
 * This happens in certain environments where stdin is not connected.
 */
export function isStdinValid(): boolean {
  try {
    const stats = statSync("/dev/stdin");
    return stats !== null;
  } catch {
    try {
      return process.stdin.readable || process.stdin.isTTY === true;
    } catch {
      return false;
    }
  }
}

export async function readJsonFromStdin(): Promise<unknown> {
  if (!isStdinValid()) {
    return undefined;
  }

  return new Promise((resolve, reject) => {
    let input = "";

    const timeout = setTimeout(() => {
      resolve(undefined);
    }, 100);

    let safetyTimeout: ReturnType<typeof setTimeout> | undefined;

    process.stdin.on("data", (chunk) => {
      clearTimeout(timeout);
      if (safetyTimeout) clearTimeout(safetyTimeout);
      input += chunk;
      safetyTimeout = setTimeout(() => {
        try {
          resolve(input.trim() ? JSON.parse(input) : undefined);
        } catch (e) {
          reject(new Error(`Failed to parse hook input: ${e}`));
        }
      }, 3000);
    });

    process.stdin.on("end", () => {
      clearTimeout(timeout);
      if (safetyTimeout) clearTimeout(safetyTimeout);
      try {
        resolve(input.trim() ? JSON.parse(input) : undefined);
      } catch (e) {
        reject(new Error(`Failed to parse hook input: ${e}`));
      }
    });

    process.stdin.on("error", () => {
      clearTimeout(timeout);
      if (safetyTimeout) clearTimeout(safetyTimeout);
      resolve(undefined);
    });
  });
}
