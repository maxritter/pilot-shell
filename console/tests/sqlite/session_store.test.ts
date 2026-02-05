/**
 * Tests for SessionStore in-memory database operations
 *
 * Mock Justification: NONE (0% mock code)
 * - Uses real SQLite with ':memory:' - tests actual SQL and schema
 * - All CRUD operations are tested against real database behavior
 * - Timestamp handling and FK relationships are validated
 *
 * Value: Validates core persistence layer without filesystem dependencies
 */
import { describe, it, expect, beforeEach, afterEach } from 'bun:test';
import { SessionStore } from '../../src/services/sqlite/SessionStore.js';

describe('SessionStore', () => {
  let store: SessionStore;

  beforeEach(() => {
    store = new SessionStore(':memory:');
  });

  afterEach(() => {
    store.close();
  });

  it('should correctly count user prompts', () => {
    const claudeId = 'claude-session-1';
    store.createSDKSession(claudeId, 'test-project', 'initial prompt');
    
    expect(store.getPromptNumberFromUserPrompts(claudeId)).toBe(0);

    store.saveUserPrompt(claudeId, 1, 'First prompt');
    expect(store.getPromptNumberFromUserPrompts(claudeId)).toBe(1);

    store.saveUserPrompt(claudeId, 2, 'Second prompt');
    expect(store.getPromptNumberFromUserPrompts(claudeId)).toBe(2);

    store.createSDKSession('claude-session-2', 'test-project', 'initial prompt');
    store.saveUserPrompt('claude-session-2', 1, 'Other prompt');
    expect(store.getPromptNumberFromUserPrompts(claudeId)).toBe(2);
  });

  it('should store observation with timestamp override', () => {
    const claudeId = 'claude-sess-obs';
    const memoryId = 'memory-sess-obs';
    const sdkId = store.createSDKSession(claudeId, 'test-project', 'initial prompt');

    store.updateMemorySessionId(sdkId, memoryId);

    const obs = {
      type: 'discovery',
      title: 'Test Obs',
      subtitle: null,
      facts: [],
      narrative: 'Testing',
      concepts: [],
      files_read: [],
      files_modified: []
    };

    const pastTimestamp = 1600000000000;

    const result = store.storeObservation(
      memoryId,
      'test-project',
      obs,
      1,
      0,
      pastTimestamp
    );

    expect(result.createdAtEpoch).toBe(pastTimestamp);

    const stored = store.getObservationById(result.id);
    expect(stored).not.toBeNull();
    expect(stored?.created_at_epoch).toBe(pastTimestamp);

    expect(new Date(stored!.created_at).getTime()).toBe(pastTimestamp);
  });

  it('should store summary with timestamp override', () => {
    const claudeId = 'claude-sess-sum';
    const memoryId = 'memory-sess-sum';
    const sdkId = store.createSDKSession(claudeId, 'test-project', 'initial prompt');

    store.updateMemorySessionId(sdkId, memoryId);

    const summary = {
      request: 'Do something',
      investigated: 'Stuff',
      learned: 'Things',
      completed: 'Done',
      next_steps: 'More',
      notes: null
    };

    const pastTimestamp = 1650000000000;

    const result = store.storeSummary(
      memoryId,
      'test-project',
      summary,
      1,
      0,
      pastTimestamp
    );

    expect(result.createdAtEpoch).toBe(pastTimestamp);

    const stored = store.getSummaryForSession(memoryId);
    expect(stored).not.toBeNull();
    expect(stored?.created_at_epoch).toBe(pastTimestamp);
  });

  it('should mark session as completed', () => {
    const claudeId = 'claude-sess-complete';
    const sdkId = store.createSDKSession(claudeId, 'test-project', 'initial prompt');

    const beforeComplete = store.db.prepare(
      'SELECT status, completed_at, completed_at_epoch FROM sdk_sessions WHERE id = ?'
    ).get(sdkId) as { status: string; completed_at: string | null; completed_at_epoch: number | null };

    expect(beforeComplete.status).toBe('active');
    expect(beforeComplete.completed_at).toBeNull();
    expect(beforeComplete.completed_at_epoch).toBeNull();

    store.markSessionCompleted(sdkId);

    const afterComplete = store.db.prepare(
      'SELECT status, completed_at, completed_at_epoch FROM sdk_sessions WHERE id = ?'
    ).get(sdkId) as { status: string; completed_at: string | null; completed_at_epoch: number | null };

    expect(afterComplete.status).toBe('completed');
    expect(afterComplete.completed_at).not.toBeNull();
    expect(afterComplete.completed_at_epoch).not.toBeNull();
    expect(afterComplete.completed_at_epoch).toBeGreaterThan(0);
  });

  it('should not update already completed sessions', () => {
    const claudeId = 'claude-sess-double-complete';
    const sdkId = store.createSDKSession(claudeId, 'test-project', 'initial prompt');

    store.markSessionCompleted(sdkId);

    const firstComplete = store.db.prepare(
      'SELECT completed_at_epoch FROM sdk_sessions WHERE id = ?'
    ).get(sdkId) as { completed_at_epoch: number };

    const originalEpoch = firstComplete.completed_at_epoch;

    store.markSessionCompleted(sdkId);

    const secondComplete = store.db.prepare(
      'SELECT completed_at_epoch FROM sdk_sessions WHERE id = ?'
    ).get(sdkId) as { completed_at_epoch: number };

    expect(secondComplete.completed_at_epoch).toBe(originalEpoch);
  });

  describe('stale session cleanup query', () => {
    it('should identify sessions with summaries using session_summaries table', () => {
      const claudeId1 = 'claude-sess-with-summary';
      const claudeId2 = 'claude-sess-without-summary';
      const memoryId1 = 'memory-sess-1';

      const sdkId1 = store.createSDKSession(claudeId1, 'test-project', 'initial prompt');
      const sdkId2 = store.createSDKSession(claudeId2, 'test-project', 'initial prompt');

      store.updateMemorySessionId(sdkId1, memoryId1);

      const summary = {
        request: 'Do something',
        investigated: 'Stuff',
        learned: 'Things',
        completed: 'Done',
        next_steps: 'More',
        notes: null
      };
      store.storeSummary(memoryId1, 'test-project', summary, 1, 0);

      const ids = [sdkId1, sdkId2];
      const placeholders = ids.map(() => '?').join(',');

      const sessionsWithSummaries = store.db.prepare(`
        SELECT DISTINCT s.id FROM sdk_sessions s
        INNER JOIN session_summaries sm ON sm.memory_session_id = s.memory_session_id
        WHERE s.id IN (${placeholders})
      `).all(...ids) as { id: number }[];

      expect(sessionsWithSummaries.length).toBe(1);
      expect(sessionsWithSummaries[0].id).toBe(sdkId1);

      const completedIds = new Set(sessionsWithSummaries.map(r => r.id));
      expect(completedIds.has(sdkId1)).toBe(true);
      expect(completedIds.has(sdkId2)).toBe(false);
    });
  });
});
