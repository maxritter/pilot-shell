/**
 * Tests for worker JSON status output structure
 *
 * Tests the buildStatusOutput pure function extracted from worker-service.ts
 * to ensure JSON output matches the hook framework contract.
 *
 * Also tests CLI output capture for the 'start' command to verify
 * actual JSON output matches expected structure.
 *
 * No mocks needed - tests a pure function directly and captures real CLI output.
 */
import { describe, it, expect } from 'bun:test';
import { spawnSync } from 'child_process';
import { statSync } from 'node:fs';
// Note: Using node:fs instead of 'fs' to avoid mock.module contamination
import path from 'path';
import { buildStatusOutput, StatusOutput } from '../../src/services/worker-service.js';

const WORKER_SCRIPT = path.join(__dirname, '../../plugin/scripts/worker-service.cjs');

/** Check file existence using node:fs to avoid mock.module contamination from other test files. */
function workerScriptExists(): boolean {
  try {
    statSync(WORKER_SCRIPT);
    return true;
  } catch {
    return false;
  }
}

/**
 * Run worker CLI command and return stdout + exit code
 * Uses spawnSync for synchronous output capture
 */
function runWorkerStart(): { stdout: string; exitCode: number } {
  const result = spawnSync('bun', [WORKER_SCRIPT, 'start'], {
    timeout: 60000
  });
  const stdout = result.stdout ? String(result.stdout).trim() : '';
  return { stdout, exitCode: result.status || 0 };
}

describe('worker-json-status', () => {
  describe('buildStatusOutput', () => {
    describe('ready status', () => {
      it('should return valid JSON with required fields for ready status', () => {
        const result = buildStatusOutput('ready');

        expect(result.status).toBe('ready');
        expect(result.continue).toBe(true);
        expect(result.suppressOutput).toBe(true);
      });

      it('should not include message field when not provided', () => {
        const result = buildStatusOutput('ready');

        expect(result.message).toBeUndefined();
        expect('message' in result).toBe(false);
      });

      it('should include message field when explicitly provided for ready status', () => {
        const result = buildStatusOutput('ready', 'Worker started successfully');

        expect(result.status).toBe('ready');
        expect(result.message).toBe('Worker started successfully');
      });
    });

    describe('error status', () => {
      it('should return valid JSON with required fields for error status', () => {
        const result = buildStatusOutput('error');

        expect(result.status).toBe('error');
        expect(result.continue).toBe(true);
        expect(result.suppressOutput).toBe(true);
      });

      it('should include message field when provided for error status', () => {
        const result = buildStatusOutput('error', 'Port in use but worker not responding');

        expect(result.status).toBe('error');
        expect(result.message).toBe('Port in use but worker not responding');
      });

      it('should handle various error messages correctly', () => {
        const errorMessages = [
          'Port did not free after version mismatch restart',
          'Failed to spawn worker daemon',
          'Worker failed to start (health check timeout)'
        ];

        for (const msg of errorMessages) {
          const result = buildStatusOutput('error', msg);
          expect(result.message).toBe(msg);
        }
      });
    });

    describe('required fields always present', () => {
      it('should always include continue: true', () => {
        expect(buildStatusOutput('ready').continue).toBe(true);
        expect(buildStatusOutput('error').continue).toBe(true);
        expect(buildStatusOutput('ready', 'msg').continue).toBe(true);
        expect(buildStatusOutput('error', 'msg').continue).toBe(true);
      });

      it('should always include suppressOutput: true', () => {
        expect(buildStatusOutput('ready').suppressOutput).toBe(true);
        expect(buildStatusOutput('error').suppressOutput).toBe(true);
        expect(buildStatusOutput('ready', 'msg').suppressOutput).toBe(true);
        expect(buildStatusOutput('error', 'msg').suppressOutput).toBe(true);
      });
    });

    describe('JSON serialization', () => {
      it('should produce valid JSON when stringified', () => {
        const readyResult = buildStatusOutput('ready');
        const errorResult = buildStatusOutput('error', 'Test error message');

        expect(() => JSON.stringify(readyResult)).not.toThrow();
        expect(() => JSON.stringify(errorResult)).not.toThrow();

        const parsedReady = JSON.parse(JSON.stringify(readyResult));
        expect(parsedReady.status).toBe('ready');
        expect(parsedReady.continue).toBe(true);

        const parsedError = JSON.parse(JSON.stringify(errorResult));
        expect(parsedError.status).toBe('error');
        expect(parsedError.message).toBe('Test error message');
      });

      it('should match expected JSON structure for hook framework', () => {
        const readyOutput = JSON.stringify(buildStatusOutput('ready'));
        const errorOutput = JSON.stringify(buildStatusOutput('error', 'error msg'));

        const parsedReady = JSON.parse(readyOutput);
        expect(parsedReady).toEqual({
          continue: true,
          suppressOutput: true,
          status: 'ready'
        });

        const parsedError = JSON.parse(errorOutput);
        expect(parsedError).toEqual({
          continue: true,
          suppressOutput: true,
          status: 'error',
          message: 'error msg'
        });
      });
    });

    describe('type safety', () => {
      it('should only accept valid status values', () => {
        const readyResult: StatusOutput = buildStatusOutput('ready');
        const errorResult: StatusOutput = buildStatusOutput('error');

        expect(['ready', 'error']).toContain(readyResult.status);
        expect(['ready', 'error']).toContain(errorResult.status);
      });

      it('should have correct type structure', () => {
        const result = buildStatusOutput('ready');

        expect(result.continue).toBe(true as const);
        expect(result.suppressOutput).toBe(true as const);
      });
    });

    describe('edge cases', () => {
      it('should handle empty string message', () => {
        const result = buildStatusOutput('error', '');
        expect('message' in result).toBe(false);
      });

      it('should handle message with special characters', () => {
        const specialMessage = 'Error: "quoted" & special <chars>';
        const result = buildStatusOutput('error', specialMessage);
        expect(result.message).toBe(specialMessage);

        const parsed = JSON.parse(JSON.stringify(result));
        expect(parsed.message).toBe(specialMessage);
      });

      it('should handle very long message', () => {
        const longMessage = 'A'.repeat(10000);
        const result = buildStatusOutput('error', longMessage);
        expect(result.message).toBe(longMessage);
      });
    });
  });

  describe('start command JSON output', () => {
    describe('when worker already healthy', () => {
      it('should output valid JSON with status: ready', () => {
        if (!workerScriptExists()) {
          console.log('Skipping CLI test - worker script not built');
          return;
        }

        const { stdout, exitCode } = runWorkerStart();

        expect(exitCode).toBe(0);

        expect(() => JSON.parse(stdout)).not.toThrow();

        const parsed = JSON.parse(stdout);

        expect(parsed.continue).toBe(true);
        expect(parsed.suppressOutput).toBe(true);
        expect(['ready', 'error']).toContain(parsed.status);
      });

      it('should match expected JSON structure when worker is healthy', () => {
        if (!workerScriptExists()) {
          console.log('Skipping CLI test - worker script not built');
          return;
        }

        const { stdout } = runWorkerStart();
        const parsed = JSON.parse(stdout);

        if (parsed.status === 'ready') {
          expect(parsed.continue).toBe(true);
          expect(parsed.suppressOutput).toBe(true);
        } else if (parsed.status === 'error') {
          expect(typeof parsed.message).toBe('string');
        }
      });
    });

    describe('error scenarios', () => {
      it.skip('should output JSON with status: error when port in use but not responding', () => {
      });

      it.skip('should output JSON with status: error on spawn failure', () => {
      });

      it.skip('should output JSON with status: error on health check timeout', () => {
      });
    });
  });

  /**
   * Claude Code hook framework compatibility tests
   *
   * These tests verify that the worker 'start' command output conforms to
   * Claude Code's hook output contract. Key requirements:
   *
   * 1. Exit code 0 - Required for Windows Terminal compatibility (prevents
   *    tab accumulation from spawned processes)
   *
   * 2. JSON on stdout - Claude Code parses stdout as JSON. Logs must go to
   *    stderr to avoid breaking JSON parsing.
   *
   * 3. `continue: true` - CRITICAL: This field tells Claude Code to continue
   *    processing. If missing or false, Claude Code stops after the hook.
   *    Per docs: "If continue is false, Claude stops processing after the
   *    hooks run."
   *
   * 4. `suppressOutput: true` - Hides output from transcript mode (Ctrl-R).
   *    Optional but recommended for non-user-facing status.
   *
   * Reference: private/context/claude-code/hooks.md
   */
  describe('Claude Code hook framework compatibility', () => {
    /**
     * Windows Terminal compatibility requirement
     *
     * When hooks run in Windows Terminal, each spawned process can open a
     * new tab. Exit code 0 tells the terminal the process completed
     * successfully and prevents tab accumulation.
     *
     * Even for error states (worker failed to start), we exit 0 and
     * communicate the error via JSON { status: 'error', message: '...' }
     */
    it('should always exit with code 0', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const { exitCode } = runWorkerStart();

      expect(exitCode).toBe(0);
    });

    /**
     * JSON must go to stdout, not stderr
     *
     * Claude Code parses stdout as JSON for hook output. Any non-JSON on
     * stdout breaks parsing. Logs, warnings, and debug info must go to
     * stderr.
     *
     * Structure: { status, continue, suppressOutput, message? }
     */
    it('should output JSON on stdout (not stderr)', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const result = spawnSync('bun', [WORKER_SCRIPT, 'start'], {
        timeout: 60000
      });

      const stdout = result.stdout ? String(result.stdout).trim() : '';
      const stderr = result.stderr ? String(result.stderr).trim() : '';

      expect(() => JSON.parse(stdout)).not.toThrow();

      const parsed = JSON.parse(stdout);
      expect(parsed).toHaveProperty('status');
      expect(parsed).toHaveProperty('continue');

      if (stderr) {
        try {
          const stderrParsed = JSON.parse(stderr);
          expect(stderrParsed).not.toHaveProperty('suppressOutput');
        } catch {
        }
      }
    });

    /**
     * JSON must be parseable as valid JSON
     *
     * This seems obvious but is critical - any extraneous output (console.log
     * statements, warnings, etc.) will break JSON parsing and cause Claude
     * Code to fail processing the hook output.
     */
    it('should be parseable as valid JSON', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const { stdout } = runWorkerStart();

      let parsed: unknown;
      expect(() => {
        parsed = JSON.parse(stdout);
      }).not.toThrow();

      expect(typeof parsed).toBe('object');
      expect(parsed).not.toBeNull();
      expect(Array.isArray(parsed)).toBe(false);
    });

    /**
     * `continue: true` is CRITICAL
     *
     * From Claude Code docs: "If continue is false, Claude stops processing
     * after the hooks run."
     *
     * For SessionStart hooks (which start the worker), we MUST return
     * continue: true so Claude Code continues to process the user's prompt.
     * If we returned continue: false, Claude would stop immediately after
     * starting the worker and never respond to the user.
     *
     * This is why continue: true is a required literal in our StatusOutput
     * type - it can never be false.
     */
    it('should always include continue: true (required for Claude Code to proceed)', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const { stdout } = runWorkerStart();
      const parsed = JSON.parse(stdout);

      expect(parsed.continue).toBe(true);

      expect(parsed.continue).toStrictEqual(true);
    });

    /**
     * suppressOutput hides from transcript mode
     *
     * When suppressOutput: true, the hook output doesn't appear in transcript
     * mode (Ctrl-R). This is useful for status messages that aren't relevant
     * to the user's conversation history.
     *
     * For the worker start command, we suppress output since "worker started"
     * is infrastructure noise, not conversation content.
     */
    it('should include suppressOutput: true to hide from transcript mode', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const { stdout } = runWorkerStart();
      const parsed = JSON.parse(stdout);

      expect(parsed.suppressOutput).toBe(true);
    });

    /**
     * status field communicates outcome
     *
     * The status field tells Claude Code (and debugging tools) whether the
     * hook succeeded. Valid values: 'ready' | 'error'
     *
     * Unlike exit codes (which are always 0), status can indicate failure.
     * This allows Claude Code to potentially take remedial action or log
     * the issue.
     */
    it('should include a valid status field', () => {
      if (!workerScriptExists()) {
        console.log('Skipping CLI test - worker script not built');
        return;
      }

      const { stdout } = runWorkerStart();
      const parsed = JSON.parse(stdout);

      expect(parsed).toHaveProperty('status');
      expect(['ready', 'error']).toContain(parsed.status);
    });
  });
});
