/**
 * Tests for project_roots table - maps projects to filesystem root paths
 *
 * Mock Justification: NONE (0% mock code)
 * - Uses real SQLite with ':memory:' - tests actual SQL and schema
 *
 * Value: Validates project root persistence and upsert behavior
 */
import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { SessionStore } from "../../src/services/sqlite/SessionStore.js";

describe("project_roots table", () => {
  let store: SessionStore;

  beforeEach(() => {
    store = new SessionStore(":memory:");
  });

  afterEach(() => {
    store.close();
  });

  it("should create project_roots table via migration", () => {
    const tables = store.db
      .query("SELECT name FROM sqlite_master WHERE type='table' AND name='project_roots'")
      .all() as Array<{ name: string }>;
    expect(tables.length).toBe(1);
    expect(tables[0].name).toBe("project_roots");
  });

  it("should insert a new project root", () => {
    store.upsertProjectRoot("my-project", "/Users/dev/my-project");

    const row = store.db
      .query("SELECT * FROM project_roots WHERE project = ?")
      .get("my-project") as { project: string; root_path: string; last_seen_at: string } | null;

    expect(row).not.toBeNull();
    expect(row!.project).toBe("my-project");
    expect(row!.root_path).toBe("/Users/dev/my-project");
    expect(row!.last_seen_at).toBeTruthy();
  });

  it("should update root_path and last_seen_at on duplicate project", () => {
    store.upsertProjectRoot("my-project", "/old/path");
    store.upsertProjectRoot("my-project", "/new/path");

    const row = store.db
      .query("SELECT * FROM project_roots WHERE project = ?")
      .get("my-project") as { project: string; root_path: string } | null;

    expect(row!.root_path).toBe("/new/path");
  });

  it("should store multiple projects independently", () => {
    store.upsertProjectRoot("project-a", "/path/a");
    store.upsertProjectRoot("project-b", "/path/b");

    const rows = store.db.query("SELECT * FROM project_roots ORDER BY project").all() as Array<{
      project: string;
      root_path: string;
    }>;

    expect(rows.length).toBe(2);
    expect(rows[0].project).toBe("project-a");
    expect(rows[1].project).toBe("project-b");
  });

  it("should return all project roots via getAllProjectRoots", () => {
    store.upsertProjectRoot("alpha", "/path/alpha");
    store.upsertProjectRoot("beta", "/path/beta");

    const roots = store.getAllProjectRoots();
    expect(roots.length).toBe(2);
    expect(roots[0].project).toBe("alpha");
    expect(roots[0].rootPath).toBe("/path/alpha");
    expect(roots[1].project).toBe("beta");
  });

  it("should return root path for a given project via getProjectRoot", () => {
    store.upsertProjectRoot("my-project", "/Users/dev/my-project");

    const root = store.getProjectRoot("my-project");
    expect(root).toBe("/Users/dev/my-project");
  });

  it("should return null for unknown project via getProjectRoot", () => {
    const root = store.getProjectRoot("nonexistent");
    expect(root).toBeNull();
  });

  it("should record migration version 23", () => {
    const version = store.db
      .query("SELECT version FROM schema_versions WHERE version = 23")
      .get() as { version: number } | null;
    expect(version).not.toBeNull();
    expect(version!.version).toBe(23);
  });
});
