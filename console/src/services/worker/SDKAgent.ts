/**
 * SDKAgent: SDK query loop handler
 *
 * Responsibility:
 * - Spawn Claude subprocess via Agent SDK
 * - Run event-driven query loop (no polling)
 * - Process SDK responses (observations, summaries)
 * - Sync to database and Chroma
 */

import { execSync } from 'child_process';
import { homedir } from 'os';
import path from 'path';
import { DatabaseManager } from './DatabaseManager.js';
import { SessionManager } from './SessionManager.js';
import { logger } from '../../utils/logger.js';
import { buildInitPrompt, buildObservationPrompt, buildSummaryPrompt, buildContinuationPrompt } from '../../sdk/prompts.js';
import { SettingsDefaultsManager } from '../../shared/SettingsDefaultsManager.js';
import { USER_SETTINGS_PATH } from '../../shared/paths.js';
import type { ActiveSession } from '../worker-types.js';
import { ModeManager } from '../domain/ModeManager.js';
import { processAgentResponse, type WorkerRef } from './agents/index.js';
import { stripApiKeyForSubscriber } from '../../shared/claude-subscription.js';

// @ts-ignore - Agent SDK types may not be available
import { unstable_v2_createSession, type SDKSession } from '@anthropic-ai/claude-agent-sdk';

import type { ModeConfig } from '../domain/types.js';

const MAX_SESSION_TOKENS = 100_000;

export class SDKAgent {
  private dbManager: DatabaseManager;
  private sessionManager: SessionManager;

  constructor(dbManager: DatabaseManager, sessionManager: SessionManager) {
    this.dbManager = dbManager;
    this.sessionManager = sessionManager;
  }

  /**
   * Start SDK agent for a session using V2 API (send/stream pattern)
   * @param worker WorkerService reference for spinner control (optional)
   */
  async startSession(session: ActiveSession, worker?: WorkerRef): Promise<void> {
    let lastCwd: string | undefined;

    const claudePath = this.findClaudeExecutable();

    const modelId = this.getModelId();
    const disallowedTools = [
      'Bash',
      'Read',
      'Write',
      'Edit',
      'Grep',
      'Glob',
      'WebFetch',
      'WebSearch',
      'Task',
      'NotebookEdit',
      'AskUserQuestion',
      'TodoWrite'
    ];

    if (!session.memorySessionId) {
      throw new Error(`Session ${session.sessionDbId} has no memory_session_id - this should not happen`);
    }

    logger.info('SDK', 'Starting SDK V2 session', {
      sessionDbId: session.sessionDbId,
      contentSessionId: session.contentSessionId,
      memorySessionId: session.memorySessionId,
      lastPromptNumber: session.lastPromptNumber
    });

    // Note: We don't use Claude's --resume because our memory_session_id is a provider-agnostic UUID,
    const restoreApiKey = stripApiKeyForSubscriber();

    let sdkSession: SDKSession = this.createSDKSession(modelId, claudePath, disallowedTools);

    try {
      const mode = ModeManager.getInstance().getActiveMode();

      const isInitPrompt = session.lastPromptNumber === 1;
      const initPrompt = isInitPrompt
        ? buildInitPrompt(session.project, session.contentSessionId, session.userPrompt, mode)
        : buildContinuationPrompt(session.userPrompt, session.lastPromptNumber, session.contentSessionId, mode);

      session.conversationHistory.push({ role: 'user', content: initPrompt });

      await sdkSession.send(initPrompt);

      await this.processStreamResponse(sdkSession, session, worker, lastCwd);

      for await (const message of this.sessionManager.getMessageIterator(session.sessionDbId)) {
        if (session.abortController.signal.aborted) {
          logger.warn('SDK', 'Session aborted', { sessionId: session.sessionDbId });
          break;
        }

        if (message.cwd) {
          lastCwd = message.cwd;
        }

        if (message.type === 'observation') {
          if (message.prompt_number !== undefined) {
            session.lastPromptNumber = message.prompt_number;
          }

          const obsPrompt = buildObservationPrompt({
            id: 0,
            tool_name: message.tool_name!,
            tool_input: JSON.stringify(message.tool_input),
            tool_output: JSON.stringify(message.tool_response),
            created_at_epoch: message._originalTimestamp ?? Date.now(),
            cwd: message.cwd
          });

          session.conversationHistory.push({ role: 'user', content: obsPrompt });

          if (session.conversationHistory.length > 12) {
            const first = session.conversationHistory.slice(0, 2);
            const last = session.conversationHistory.slice(-10);
            session.conversationHistory.length = 0;
            session.conversationHistory.push(...first, ...last);
          }

          await sdkSession.send(obsPrompt);
          await this.processStreamResponse(sdkSession, session, worker, lastCwd);

          sdkSession = await this.maybeRotateSession(
            sdkSession, session, modelId, claudePath, disallowedTools, mode, worker, lastCwd
          );

        } else if (message.type === 'summarize') {
          const summaryPrompt = buildSummaryPrompt({
            id: session.sessionDbId,
            memory_session_id: session.memorySessionId,
            project: session.project,
            user_prompt: session.userPrompt,
            last_assistant_message: message.last_assistant_message || ''
          }, mode);

          session.conversationHistory.push({ role: 'user', content: summaryPrompt });

          await sdkSession.send(summaryPrompt);
          await this.processStreamResponse(sdkSession, session, worker, lastCwd);

          sdkSession = await this.maybeRotateSession(
            sdkSession, session, modelId, claudePath, disallowedTools, mode, worker, lastCwd
          );
        }
      }

      const sessionDuration = Date.now() - session.startTime;
      logger.success('SDK', 'V2 Agent completed', {
        sessionId: session.sessionDbId,
        duration: `${(sessionDuration / 1000).toFixed(1)}s`
      });

    } finally {
      sdkSession.close();

      if (restoreApiKey) {
        restoreApiKey();
      }
    }
  }

  /**
   * Process stream response from V2 session
   * Handles message capture, token tracking, and response processing
   */
  private async processStreamResponse(
    sdkSession: SDKSession,
    session: ActiveSession,
    worker: WorkerRef | undefined,
    lastCwd: string | undefined
  ): Promise<void> {
    const originalTimestamp = session.earliestPendingTimestamp;

    for await (const message of sdkSession.stream()) {
      // Note: memory_session_id is now generated at session creation time (provider-agnostic UUID)

      if (message.type === 'assistant') {
        const content = message.message.content;
        const textContent = Array.isArray(content)
          ? content.filter((c: any) => c.type === 'text').map((c: any) => c.text).join('\n')
          : typeof content === 'string' ? content : '';

        const responseSize = textContent.length;

        const tokensBeforeResponse = session.cumulativeInputTokens + session.cumulativeOutputTokens;

        const usage = message.message.usage;
        if (usage) {
          session.cumulativeInputTokens += usage.input_tokens || 0;
          session.cumulativeOutputTokens += usage.output_tokens || 0;

          if (usage.cache_creation_input_tokens) {
            session.cumulativeInputTokens += usage.cache_creation_input_tokens;
          }

          logger.debug('SDK', 'Token usage captured', {
            sessionId: session.sessionDbId,
            inputTokens: usage.input_tokens,
            outputTokens: usage.output_tokens,
            cumulativeInput: session.cumulativeInputTokens,
            cumulativeOutput: session.cumulativeOutputTokens
          });
        }

        const discoveryTokens = (session.cumulativeInputTokens + session.cumulativeOutputTokens) - tokensBeforeResponse;

        if (responseSize > 0) {
          const truncatedResponse = responseSize > 100
            ? textContent.substring(0, 100) + '...'
            : textContent;
          logger.dataOut('SDK', `V2 Response received (${responseSize} chars)`, {
            sessionId: session.sessionDbId,
            promptNumber: session.lastPromptNumber
          }, truncatedResponse);
        }

        await processAgentResponse(
          textContent,
          session,
          this.dbManager,
          this.sessionManager,
          worker,
          discoveryTokens,
          originalTimestamp,
          'SDK',
          lastCwd
        );
      }
    }
  }


  /**
   * Create a new SDK session with the given configuration.
   */
  private createSDKSession(modelId: string, claudePath: string, disallowedTools: string[]): SDKSession {
    return unstable_v2_createSession({
      model: modelId,
      disallowedTools,
      pathToClaudeCodeExecutable: claudePath
    });
  }

  /**
   * Check if SDK session needs rotation due to token accumulation.
   * Returns new session if rotated, or same session if not needed.
   */
  private async maybeRotateSession(
    currentSession: SDKSession,
    session: ActiveSession,
    modelId: string,
    claudePath: string,
    disallowedTools: string[],
    mode: ModeConfig,
    worker: WorkerRef | undefined,
    lastCwd: string | undefined
  ): Promise<SDKSession> {
    const totalTokens = session.cumulativeInputTokens + session.cumulativeOutputTokens;

    if (totalTokens <= MAX_SESSION_TOKENS) {
      return currentSession;
    }

    logger.info('SDK', 'Rotating SDK session due to token limit', {
      totalTokens,
      threshold: MAX_SESSION_TOKENS
    });

    try {
      currentSession.close();
    } catch (closeError) {
      logger.warn('SDK', 'Error closing session during rotation', {}, closeError as Error);
    }

    const newSession = this.createSDKSession(modelId, claudePath, disallowedTools);

    const freshInitPrompt = buildContinuationPrompt(
      session.userPrompt,
      session.lastPromptNumber,
      session.contentSessionId,
      mode
    );
    await newSession.send(freshInitPrompt);
    await this.processStreamResponse(newSession, session, worker, lastCwd);

    session.cumulativeInputTokens = 0;
    session.cumulativeOutputTokens = 0;

    return newSession;
  }

  /**
   * Find Claude executable (inline, called once per session)
   */
  private findClaudeExecutable(): string {
    const settings = SettingsDefaultsManager.loadFromFile(USER_SETTINGS_PATH);

    if (settings.CLAUDE_CODE_PATH) {
      const { existsSync } = require('fs');
      if (!existsSync(settings.CLAUDE_CODE_PATH)) {
        throw new Error(`CLAUDE_CODE_PATH is set to "${settings.CLAUDE_CODE_PATH}" but the file does not exist.`);
      }
      return settings.CLAUDE_CODE_PATH;
    }

    try {
      const claudePath = execSync(
        process.platform === 'win32' ? 'where claude' : 'which claude',
        { encoding: 'utf8', windowsHide: true, stdio: ['ignore', 'pipe', 'ignore'] }
      ).trim().split('\n')[0].trim();

      if (claudePath) return claudePath;
    } catch (error) {
      logger.debug('SDK', 'Claude executable auto-detection failed', {}, error as Error);
    }

    throw new Error('Claude executable not found. Please either:\n1. Add "claude" to your system PATH, or\n2. Set CLAUDE_CODE_PATH in ~/.pilot/memory/settings.json');
  }

  /**
   * Get model ID from settings or environment
   */
  private getModelId(): string {
    const settingsPath = path.join(homedir(), '.pilot/memory', 'settings.json');
    const settings = SettingsDefaultsManager.loadFromFile(settingsPath);
    return settings.CLAUDE_PILOT_MODEL;
  }
}
