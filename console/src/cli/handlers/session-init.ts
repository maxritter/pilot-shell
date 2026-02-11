/**
 * Session Init Handler - UserPromptSubmit
 *
 * Extracted from new-hook.ts - initializes session and starts SDK agent.
 */

import type { EventHandler, NormalizedHookInput, HookResult } from "../types.js";
import { getWorkerEndpointConfig } from "../../shared/remote-endpoint.js";
import { fetchWithAuth } from "../../shared/fetch-with-auth.js";
import { isProjectExcluded, isMemoryDisabledByProjectConfig } from "../../shared/project-exclusion.js";
import { getProjectName } from "../../utils/project-name.js";
import { logger } from "../../utils/logger.js";

export const sessionInitHandler: EventHandler = {
  async execute(input: NormalizedHookInput): Promise<HookResult> {
    const endpointConfig = getWorkerEndpointConfig();
    const { sessionId, cwd, prompt } = input;

    if (!prompt) {
      logger.debug("HOOK", "session-init: Empty prompt received, skipping session initialization");
      return { continue: true, suppressOutput: true };
    }

    const project = getProjectName(cwd);

    if (isMemoryDisabledByProjectConfig(cwd)) {
      logger.debug("HOOK", "session-init: Memory disabled by .pilot/memory.json", { project, cwd });
      return { continue: true, suppressOutput: true };
    }

    if (isProjectExcluded(project)) {
      logger.debug("HOOK", "session-init: Project excluded by CLAUDE_PILOT_EXCLUDE_PROJECTS", { project });
      return { continue: true, suppressOutput: true };
    }

    logger.debug("HOOK", "session-init: Calling /api/sessions/init", {
      contentSessionId: sessionId,
      project,
      mode: endpointConfig.mode,
    });

    const initResponse = await fetchWithAuth(
      `${endpointConfig.baseUrl}/api/sessions/init`,
      {
        method: "POST",
        body: JSON.stringify({
          contentSessionId: sessionId,
          project,
          prompt,
          projectRoot: cwd,
        }),
      },
      { endpointConfig },
    );

    if (!initResponse.ok) {
      throw new Error(`Session initialization failed: ${initResponse.status}`);
    }

    const initResult = (await initResponse.json()) as {
      sessionDbId: number;
      promptNumber: number;
      skipped?: boolean;
      reason?: string;
    };
    const sessionDbId = initResult.sessionDbId;
    const promptNumber = initResult.promptNumber;

    logger.debug("HOOK", "session-init: Received from /api/sessions/init", {
      sessionDbId,
      promptNumber,
      skipped: initResult.skipped,
    });

    logger.debug(
      "HOOK",
      `[ALIGNMENT] Hook Entry | contentSessionId=${sessionId} | prompt#=${promptNumber} | sessionDbId=${sessionDbId}`,
    );

    if (initResult.skipped && initResult.reason === "private") {
      logger.info(
        "HOOK",
        `INIT_COMPLETE | sessionDbId=${sessionDbId} | promptNumber=${promptNumber} | skipped=true | reason=private`,
        {
          sessionId: sessionDbId,
        },
      );
      return { continue: true, suppressOutput: true };
    }

    if (sessionDbId) {
      const cleanedPrompt = prompt.startsWith("/") ? prompt.substring(1) : prompt;

      logger.debug("HOOK", "session-init: Calling /sessions/{sessionDbId}/init", { sessionDbId, promptNumber });

      const response = await fetchWithAuth(
        `${endpointConfig.baseUrl}/sessions/${sessionDbId}/init`,
        {
          method: "POST",
          body: JSON.stringify({ userPrompt: cleanedPrompt, promptNumber }),
        },
        { endpointConfig },
      );

      if (!response.ok) {
        throw new Error(`SDK agent start failed: ${response.status}`);
      }
    }

    logger.info(
      "HOOK",
      `INIT_COMPLETE | sessionDbId=${sessionDbId} | promptNumber=${promptNumber} | project=${project}`,
      {
        sessionId: sessionDbId,
      },
    );

    return { continue: true, suppressOutput: true };
  },
};
