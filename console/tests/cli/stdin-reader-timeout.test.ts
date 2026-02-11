/**
 * Tests for stdin safety timeout after data starts
 *
 * Mock Justification:
 * - process.stdin: Required because we can't control real stdin timing in tests.
 *   We create a mock EventEmitter to simulate data arriving without "end" event.
 */
import { describe, it, expect, mock, beforeEach, afterEach } from "bun:test";
import { EventEmitter } from "events";

let mockStdin: EventEmitter & { readable?: boolean; isTTY?: boolean };
let originalStdin: typeof process.stdin;

describe("stdin safety timeout", () => {
  beforeEach(() => {
    mockStdin = new EventEmitter() as EventEmitter & {
      readable?: boolean;
      isTTY?: boolean;
    };
    mockStdin.readable = true;
    originalStdin = process.stdin;
    // @ts-expect-error - replacing stdin for testing
    process.stdin = mockStdin;
  });

  afterEach(() => {
    process.stdin = originalStdin;
    mock.restore();
  });

  it("should resolve with parsed JSON when data arrives and end fires normally", async () => {
    const { readJsonFromStdin } = await import("../../src/cli/stdin-reader.js");

    const promise = readJsonFromStdin();

    mockStdin.emit("data", '{"test": true}');
    mockStdin.emit("end");

    const result = await promise;
    expect(result).toEqual({ test: true });
  });

  it("should resolve within 3 seconds when data arrives but end never fires", async () => {
    const { readJsonFromStdin } = await import("../../src/cli/stdin-reader.js");

    const start = Date.now();
    const promise = readJsonFromStdin();

    mockStdin.emit("data", '{"partial": true}');

    const result = await promise;
    const elapsed = Date.now() - start;

    expect(result).toEqual({ partial: true });
    expect(elapsed).toBeLessThan(4000);
  });

  it("should resolve with undefined when no data arrives (100ms timeout)", async () => {
    const { readJsonFromStdin } = await import("../../src/cli/stdin-reader.js");

    const start = Date.now();
    const result = await readJsonFromStdin();
    const elapsed = Date.now() - start;

    expect(result).toBeUndefined();
    expect(elapsed).toBeLessThan(500);
  });
});
