/**
 * Tests for observation type constraint removal
 *
 * Verifies that custom observation types can be inserted without CHECK constraint errors.
 *
 * Mock Justification:
 * - Logger spies: Suppress output during tests
 * - No other mocks: Uses real in-memory SQLite database
 */
import { describe, it, expect, beforeEach, afterEach, spyOn } from "bun:test";
import { Database } from "bun:sqlite";
import { logger } from "../../src/utils/logger.js";
import { MigrationRunner } from "../../src/services/sqlite/migrations/runner.js";

let loggerSpies: ReturnType<typeof spyOn>[] = [];

describe("Observation type constraint removal", () => {
  let db: Database;

  beforeEach(() => {
    db = new Database(":memory:");
    loggerSpies = [
      spyOn(logger, "info").mockImplementation(() => {}),
      spyOn(logger, "debug").mockImplementation(() => {}),
      spyOn(logger, "warn").mockImplementation(() => {}),
      spyOn(logger, "error").mockImplementation(() => {}),
    ];
  });

  afterEach(() => {
    loggerSpies.forEach((spy) => spy.mockRestore());
    db.close();
  });

  it("should allow custom observation types on fresh database", () => {
    const runner = new MigrationRunner(db);
    runner.runAllMigrations();

    db.run(
      `INSERT INTO sdk_sessions (content_session_id, memory_session_id, project, started_at, started_at_epoch)
       VALUES ('cs-1', 'ms-1', 'test', '2024-01-01', 1704067200)`,
    );

    expect(() => {
      db.run(
        `INSERT INTO observations (memory_session_id, project, text, type, created_at, created_at_epoch)
         VALUES ('ms-1', 'test', 'custom obs', 'skill-learning', '2024-01-01', 1704067200)`,
      );
    }).not.toThrow();
  });

  it("should still allow standard observation types", () => {
    const runner = new MigrationRunner(db);
    runner.runAllMigrations();

    db.run(
      `INSERT INTO sdk_sessions (content_session_id, memory_session_id, project, started_at, started_at_epoch)
       VALUES ('cs-1', 'ms-1', 'test', '2024-01-01', 1704067200)`,
    );

    for (const type of ["decision", "bugfix", "feature", "refactor", "discovery", "change"]) {
      expect(() => {
        db.run(
          `INSERT INTO observations (memory_session_id, project, text, type, created_at, created_at_epoch)
           VALUES ('ms-1', 'test', 'obs', ?, '2024-01-01', 1704067200)`,
          [type],
        );
      }).not.toThrow();
    }
  });

  it("should remove CHECK constraint from existing databases via migration", () => {
    db.run(`
      CREATE TABLE schema_versions (
        id INTEGER PRIMARY KEY,
        version INTEGER UNIQUE NOT NULL,
        applied_at TEXT NOT NULL
      )
    `);
    db.run(`
      CREATE TABLE sdk_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_session_id TEXT UNIQUE NOT NULL,
        memory_session_id TEXT UNIQUE,
        project TEXT NOT NULL,
        user_prompt TEXT,
        started_at TEXT NOT NULL,
        started_at_epoch INTEGER NOT NULL,
        completed_at TEXT,
        completed_at_epoch INTEGER,
        status TEXT CHECK(status IN ('active', 'completed', 'failed')) NOT NULL DEFAULT 'active',
        worker_port INTEGER,
        prompt_counter INTEGER DEFAULT 0
      )
    `);
    db.run(`
      CREATE TABLE observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_session_id TEXT NOT NULL,
        project TEXT NOT NULL,
        text TEXT,
        type TEXT NOT NULL CHECK(type IN ('decision', 'bugfix', 'feature', 'refactor', 'discovery', 'change')),
        title TEXT, subtitle TEXT, facts TEXT, narrative TEXT, concepts TEXT,
        files_read TEXT, files_modified TEXT, prompt_number INTEGER,
        discovery_tokens INTEGER DEFAULT 0, tags TEXT,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `);
    db.run(`
      CREATE TABLE session_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_session_id TEXT NOT NULL,
        project TEXT NOT NULL,
        request TEXT, investigated TEXT, learned TEXT, completed TEXT,
        next_steps TEXT, files_read TEXT, files_edited TEXT, notes TEXT,
        prompt_number INTEGER, discovery_tokens INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `);

    for (const v of [4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 19, 20, 21]) {
      db.run("INSERT INTO schema_versions (version, applied_at) VALUES (?, ?)", [v, new Date().toISOString()]);
    }

    db.run(
      `INSERT INTO sdk_sessions (content_session_id, memory_session_id, project, started_at, started_at_epoch)
       VALUES ('cs-1', 'ms-1', 'test', '2024-01-01', 1704067200)`,
    );
    db.run(
      `INSERT INTO observations (memory_session_id, project, text, type, created_at, created_at_epoch)
       VALUES ('ms-1', 'test', 'existing obs', 'bugfix', '2024-01-01', 1704067200)`,
    );

    const runner = new MigrationRunner(db);
    runner.runAllMigrations();

    expect(() => {
      db.run(
        `INSERT INTO observations (memory_session_id, project, text, type, created_at, created_at_epoch)
         VALUES ('ms-1', 'test', 'custom', 'mode-specific', '2024-01-01', 1704067200)`,
      );
    }).not.toThrow();

    const count = db.query("SELECT COUNT(*) as cnt FROM observations").get() as { cnt: number };
    expect(count.cnt).toBe(2);
  });
});
