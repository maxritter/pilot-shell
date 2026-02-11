/**
 * Tests for hook fail-open behavior when worker is unavailable
 *
 * Mock Justification:
 * - getPlatformAdapter/getEventHandler: Required to simulate worker unavailability
 * - readJsonFromStdin: Required to avoid real stdin reads
 * - process.exit: Must intercept to verify exit code without killing test process
 * - console.log/error: Capture output for verification
 */
import { describe, it, expect, mock, beforeEach, afterEach, spyOn } from "bun:test";

const mockReadJsonFromStdin = mock(() => Promise.resolve({}));
const mockGetPlatformAdapter = mock(() => ({
  normalizeInput: (raw: unknown) => ({ sessionId: "test", cwd: "/tmp", ...raw as object }),
  formatOutput: (result: unknown) => result,
}));
const mockExecute = mock((): Promise<Record<string, unknown>> => Promise.reject(new Error("ECONNREFUSED")));
const mockGetEventHandler = mock(() => ({ execute: mockExecute }));

mock.module("../src/cli/stdin-reader.js", () => ({
  readJsonFromStdin: mockReadJsonFromStdin,
}));
mock.module("../src/cli/adapters/index.js", () => ({
  getPlatformAdapter: mockGetPlatformAdapter,
}));
mock.module("../src/cli/handlers/index.js", () => ({
  getEventHandler: mockGetEventHandler,
}));

describe("hookCommand fail-open", () => {
  let exitSpy: ReturnType<typeof spyOn>;
  let logSpy: ReturnType<typeof spyOn>;
  let errorSpy: ReturnType<typeof spyOn>;

  beforeEach(() => {
    exitSpy = spyOn(process, "exit").mockImplementation(() => undefined as never);
    logSpy = spyOn(console, "log").mockImplementation(() => {});
    errorSpy = spyOn(console, "error").mockImplementation(() => {});
    mockExecute.mockReset();
  });

  afterEach(() => {
    exitSpy.mockRestore();
    logSpy.mockRestore();
    errorSpy.mockRestore();
    mock.restore();
  });

  it("should exit with code 0 when handler throws (worker unavailable)", async () => {
    mockExecute.mockRejectedValue(new Error("ECONNREFUSED"));

    const { hookCommand } = await import("../../src/cli/hook-command.js");
    await hookCommand("claude", "observation");

    expect(exitSpy).toHaveBeenCalledWith(0);
  });

  it("should output valid JSON with continue: true on error", async () => {
    mockExecute.mockRejectedValue(new Error("ECONNREFUSED"));

    const { hookCommand } = await import("../../src/cli/hook-command.js");
    await hookCommand("claude", "observation");

    expect(logSpy).toHaveBeenCalled();
    const output = JSON.parse(logSpy.mock.calls[0][0]);
    expect(output.continue).toBe(true);
  });

  it("should still log the error to stderr", async () => {
    mockExecute.mockRejectedValue(new Error("Worker not running"));

    const { hookCommand } = await import("../../src/cli/hook-command.js");
    await hookCommand("claude", "observation");

    expect(errorSpy).toHaveBeenCalled();
  });

  it("should return hookSpecificOutput with empty additionalContext for context event", async () => {
    mockExecute.mockRejectedValue(new Error("ECONNREFUSED"));

    const { hookCommand } = await import("../../src/cli/hook-command.js");
    await hookCommand("claude", "context");

    expect(logSpy).toHaveBeenCalled();
    const output = JSON.parse(logSpy.mock.calls[0][0]);
    expect(output.hookSpecificOutput).toBeDefined();
    expect(output.hookSpecificOutput.hookEventName).toBe("SessionStart");
    expect(output.hookSpecificOutput.additionalContext).toBe("");
    expect(exitSpy).toHaveBeenCalledWith(0);
  });

  it("should succeed normally when handler works", async () => {
    mockExecute.mockResolvedValue({ continue: true, suppressOutput: true });

    const { hookCommand } = await import("../../src/cli/hook-command.js");
    await hookCommand("claude", "observation");

    expect(exitSpy).toHaveBeenCalledWith(0);
  });
});
