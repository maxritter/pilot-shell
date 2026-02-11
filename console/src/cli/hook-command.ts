import { readJsonFromStdin } from "./stdin-reader.js";
import { getPlatformAdapter } from "./adapters/index.js";
import { getEventHandler, type EventType } from "./handlers/index.js";
import { HOOK_EXIT_CODES } from "../shared/hook-constants.js";

export async function hookCommand(platform: string, event: string): Promise<void> {
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
    console.error(`Hook error (fail-open): ${error}`);
    if (event === "context") {
      console.log(JSON.stringify({ hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: "" } }));
    } else {
      console.log(JSON.stringify({ continue: true, suppressOutput: true }));
    }
    process.exit(HOOK_EXIT_CODES.SUCCESS);
  }
}
