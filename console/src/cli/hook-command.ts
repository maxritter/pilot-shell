import { readJsonFromStdin } from "./stdin-reader.js";
import { getPlatformAdapter } from "./adapters/index.js";
import { getEventHandler, type EventType } from "./handlers/index.js";
import { HOOK_EXIT_CODES } from "../shared/hook-constants.js";
import { logger } from "../utils/logger.js";

export async function hookCommand(
  platform: string,
  event: string,
): Promise<void> {
  try {
    const adapter = getPlatformAdapter(platform);
    const handler = getEventHandler(event as EventType);

    const rawInput = await readJsonFromStdin();
    const input = adapter.normalizeInput(rawInput);
    input.platform = platform;
    const result = await handler.execute(input);
    const output = adapter.formatOutput(result);

    console.log(JSON.stringify(output));
    process.exit(result.exitCode ?? HOOK_EXIT_CODES.SUCCESS);
  } catch (error) {
    // Log to file only — never dump to stderr. Hooks are fail-open by design,
    // and stderr output appears as red text in the terminal, pollutes Claude's
    // context, and can block the user when the error contains HTML (e.g.,
    // Cloudflare challenge pages from remote worker endpoints).
    const message = error instanceof Error ? error.message : String(error);
    logger.debug(
      "HOOK",
      `Hook error (fail-open) [${event}]: ${message.slice(0, 200)}`,
    );
    if (event === "context") {
      console.log(
        JSON.stringify({
          hookSpecificOutput: {
            hookEventName: "SessionStart",
            additionalContext: "",
          },
        }),
      );
    } else {
      console.log(JSON.stringify({ continue: true, suppressOutput: true }));
    }
    process.exit(HOOK_EXIT_CODES.SUCCESS);
  }
}
