/**
 * Tests for FK safety during table-recreation migrations
 *
 * Verifies that migrations 7 and 9 disable FK checks before table recreation
 * to handle orphaned rows gracefully.
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

describe("Migration FK safety", () => {
  let db: Database;

  beforeEach(() => {
    db = new Database(":memory:");
    db.run("PRAGMA foreign_keys = ON");
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

  it("should succeed when orphaned session_summaries exist (migration 7)", () => {
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
        text TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('decision', 'bugfix', 'feature', 'refactor', 'discovery')),
        prompt_number INTEGER,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `);
    db.run(`
      CREATE TABLE session_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_session_id TEXT UNIQUE NOT NULL,
        project TEXT NOT NULL,
        request TEXT,
        investigated TEXT,
        learned TEXT,
        completed TEXT,
        next_steps TEXT,
        files_read TEXT,
        files_edited TEXT,
        notes TEXT,
        prompt_number INTEGER,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `);

    for (const v of [4, 5, 6]) {
      db.run("INSERT INTO schema_versions (version, applied_at) VALUES (?, ?)", [v, new Date().toISOString()]);
    }

    db.run("PRAGMA foreign_keys = OFF");
    db.run(
      `INSERT INTO session_summaries (memory_session_id, project, created_at, created_at_epoch)
       VALUES ('orphaned-session', 'test', '2024-01-01', 1704067200)`,
    );
    db.run("PRAGMA foreign_keys = ON");

    const runner = new MigrationRunner(db);
    expect(() => runner.runAllMigrations()).not.toThrow();

    const v7 = db.query("SELECT version FROM schema_versions WHERE version = 7").get();
    expect(v7).toBeTruthy();
  });

  it("should succeed when orphaned observations exist (migration 9)", () => {
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
        text TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('decision', 'bugfix', 'feature', 'refactor', 'discovery')),
        title TEXT,
        subtitle TEXT,
        facts TEXT,
        narrative TEXT,
        concepts TEXT,
        files_read TEXT,
        files_modified TEXT,
        prompt_number INTEGER,
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
        request TEXT,
        investigated TEXT,
        learned TEXT,
        completed TEXT,
        next_steps TEXT,
        files_read TEXT,
        files_edited TEXT,
        notes TEXT,
        prompt_number INTEGER,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `);

    for (const v of [4, 5, 6, 7, 8]) {
      db.run("INSERT INTO schema_versions (version, applied_at) VALUES (?, ?)", [v, new Date().toISOString()]);
    }

    db.run("PRAGMA foreign_keys = OFF");
    db.run(
      `INSERT INTO observations (memory_session_id, project, text, type, created_at, created_at_epoch)
       VALUES ('orphaned-session', 'test', 'orphaned obs', 'bugfix', '2024-01-01', 1704067200)`,
    );
    db.run("PRAGMA foreign_keys = ON");

    const runner = new MigrationRunner(db);
    expect(() => runner.runAllMigrations()).not.toThrow();

    const v9 = db.query("SELECT version FROM schema_versions WHERE version = 9").get();
    expect(v9).toBeTruthy();
  });

  it("should re-enable FK checks after migration completes", () => {
    const runner = new MigrationRunner(db);
    runner.runAllMigrations();

    const fkStatus = db.query("PRAGMA foreign_keys").get() as { foreign_keys: number };
    expect(fkStatus.foreign_keys).toBe(1);
  });
});
