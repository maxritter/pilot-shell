/**
 * Tests for session cleanup helper functionality
 *
 * Mock Justification (~19% mock code):
 * - Session fixtures: Required to create valid ActiveSession objects with
 *   all required fields - tests the actual cleanup logic
 * - Worker mocks: Verify broadcast notification calls - the actual
 *   cleanupProcessedMessages logic is tested against real session mutation
 *
 * What's NOT mocked: Session state mutation, null/undefined handling
 */
import { describe, it, expect, mock } from 'bun:test';

import { cleanupProcessedMessages } from '../../../src/services/worker/agents/SessionCleanupHelper.js';
import type { WorkerRef } from '../../../src/services/worker/agents/types.js';
import type { ActiveSession } from '../../../src/services/worker-types.js';

describe('SessionCleanupHelper', () => {
  function createMockSession(
    overrides: Partial<ActiveSession> = {}
  ): ActiveSession {
    return {
      sessionDbId: 1,
      contentSessionId: 'content-session-123',
      memorySessionId: 'memory-session-456',
      project: 'test-project',
      userPrompt: 'Test prompt',
      pendingMessages: [],
      abortController: new AbortController(),
      generatorPromise: null,
      lastPromptNumber: 5,
      startTime: Date.now(),
      lastActivityTime: Date.now(),
      cumulativeInputTokens: 100,
      cumulativeOutputTokens: 50,
      earliestPendingTimestamp: Date.now() - 10000,
      conversationHistory: [],
      currentProvider: 'claude',
      consecutiveRestarts: 0,
      ...overrides,
    };
  }

  function createMockWorker() {
    const broadcastProcessingStatusMock = mock(() => {});
    const worker: WorkerRef = {
      sseBroadcaster: {
        broadcast: mock(() => {}),
      },
      broadcastProcessingStatus: broadcastProcessingStatusMock,
    };
    return { worker, broadcastProcessingStatusMock };
  }

  describe('cleanupProcessedMessages', () => {
    it('should reset session.earliestPendingTimestamp to null', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
      });
      const { worker } = createMockWorker();

      expect(session.earliestPendingTimestamp).toBe(1700000000000);

      cleanupProcessedMessages(session, worker);

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should reset earliestPendingTimestamp even when already null', () => {
      const session = createMockSession({
        earliestPendingTimestamp: null,
      });
      const { worker } = createMockWorker();

      cleanupProcessedMessages(session, worker);

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should call worker.broadcastProcessingStatus() if available', () => {
      const session = createMockSession();
      const { worker, broadcastProcessingStatusMock } = createMockWorker();

      cleanupProcessedMessages(session, worker);

      expect(broadcastProcessingStatusMock).toHaveBeenCalledTimes(1);
    });

    it('should handle missing worker gracefully (no crash)', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
      });

      expect(() => {
        cleanupProcessedMessages(session, undefined);
      }).not.toThrow();

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should handle worker without broadcastProcessingStatus', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
      });
      const worker: WorkerRef = {
        sseBroadcaster: {
          broadcast: mock(() => {}),
        },
      };

      expect(() => {
        cleanupProcessedMessages(session, worker);
      }).not.toThrow();

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should handle empty worker object', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
      });
      const worker: WorkerRef = {};

      expect(() => {
        cleanupProcessedMessages(session, worker);
      }).not.toThrow();

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should handle worker with null broadcastProcessingStatus', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
      });
      const worker: WorkerRef = {
        broadcastProcessingStatus: undefined,
      };

      expect(() => {
        cleanupProcessedMessages(session, worker);
      }).not.toThrow();

      expect(session.earliestPendingTimestamp).toBeNull();
    });

    it('should not modify other session properties', () => {
      const session = createMockSession({
        earliestPendingTimestamp: 1700000000000,
        lastPromptNumber: 10,
        cumulativeInputTokens: 500,
        cumulativeOutputTokens: 250,
        project: 'my-project',
      });
      const { worker } = createMockWorker();

      cleanupProcessedMessages(session, worker);

      expect(session.earliestPendingTimestamp).toBeNull();
      expect(session.lastPromptNumber).toBe(10);
      expect(session.cumulativeInputTokens).toBe(500);
      expect(session.cumulativeOutputTokens).toBe(250);
      expect(session.project).toBe('my-project');
    });
  });
});
