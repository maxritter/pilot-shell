import { describe, it, expect, beforeEach, afterEach, mock } from 'bun:test';
import {
  isPortInUse,
  waitForHealth,
  waitForPortFree
} from '../../src/services/infrastructure/index.js';

describe('HealthMonitor', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('isPortInUse', () => {
    it('should return true for occupied port (health check succeeds)', async () => {
      global.fetch = mock(() => Promise.resolve({ ok: true } as Response)) as unknown as typeof fetch;

      const result = await isPortInUse(41777);

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith('http://127.0.0.1:41777/api/health', {});
    });

    it('should return false for free port (connection refused)', async () => {
      global.fetch = mock(() => Promise.reject(new Error('ECONNREFUSED'))) as unknown as typeof fetch;

      const result = await isPortInUse(39999);

      expect(result).toBe(false);
    });

    it('should return false when health check returns non-ok', async () => {
      global.fetch = mock(() => Promise.resolve({ ok: false, status: 503 } as Response)) as unknown as typeof fetch;

      const result = await isPortInUse(41777);

      expect(result).toBe(false);
    });

    it('should return false on network timeout', async () => {
      global.fetch = mock(() => Promise.reject(new Error('ETIMEDOUT'))) as unknown as typeof fetch;

      const result = await isPortInUse(41777);

      expect(result).toBe(false);
    });

    it('should return false on fetch failed error', async () => {
      global.fetch = mock(() => Promise.reject(new Error('fetch failed'))) as unknown as typeof fetch;

      const result = await isPortInUse(41777);

      expect(result).toBe(false);
    });
  });

  describe('waitForHealth', () => {
    it('should succeed immediately when server responds', async () => {
      global.fetch = mock(() => Promise.resolve({ ok: true } as Response)) as unknown as typeof fetch;

      const start = Date.now();
      const result = await waitForHealth(41777, 5000);
      const elapsed = Date.now() - start;

      expect(result).toBe(true);
      expect(elapsed).toBeLessThan(1000);
    });

    it('should timeout when no server responds', async () => {
      global.fetch = mock(() => Promise.reject(new Error('ECONNREFUSED'))) as unknown as typeof fetch;

      const start = Date.now();
      const result = await waitForHealth(39999, 1500);
      const elapsed = Date.now() - start;

      expect(result).toBe(false);
      expect(elapsed).toBeGreaterThanOrEqual(1400);
      expect(elapsed).toBeLessThan(2500);
    });

    it('should succeed after server becomes available', async () => {
      let callCount = 0;
      global.fetch = mock(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.reject(new Error('ECONNREFUSED'));
        }
        return Promise.resolve({ ok: true } as Response);
      }) as unknown as typeof fetch;

      const result = await waitForHealth(41777, 5000);

      expect(result).toBe(true);
      expect(callCount).toBeGreaterThanOrEqual(3);
    });

    it('should check readiness endpoint not health endpoint', async () => {
      const fetchMock = mock(() => Promise.resolve({ ok: true } as Response));
      global.fetch = fetchMock as unknown as typeof fetch;

      await waitForHealth(41777, 1000);

      const calls = fetchMock.mock.calls as unknown[][];
      expect(calls.length).toBeGreaterThan(0);
      expect(calls[0][0]).toBe('http://127.0.0.1:41777/api/readiness');
    });

    it('should use default timeout when not specified', async () => {
      global.fetch = mock(() => Promise.resolve({ ok: true } as Response)) as unknown as typeof fetch;

      const result = await waitForHealth(41777);

      expect(result).toBe(true);
    });
  });

  describe('waitForPortFree', () => {
    it('should return true immediately when port is already free', async () => {
      global.fetch = mock(() => Promise.reject(new Error('ECONNREFUSED'))) as unknown as typeof fetch;

      const start = Date.now();
      const result = await waitForPortFree(39999, 5000);
      const elapsed = Date.now() - start;

      expect(result).toBe(true);
      expect(elapsed).toBeLessThan(1000);
    });

    it('should timeout when port remains occupied', async () => {
      global.fetch = mock(() => Promise.resolve({ ok: true } as Response)) as unknown as typeof fetch;

      const start = Date.now();
      const result = await waitForPortFree(41777, 1500);
      const elapsed = Date.now() - start;

      expect(result).toBe(false);
      expect(elapsed).toBeGreaterThanOrEqual(1400);
      expect(elapsed).toBeLessThan(2500);
    });

    it('should succeed when port becomes free', async () => {
      let callCount = 0;
      global.fetch = mock(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.resolve({ ok: true } as Response);
        }
        return Promise.reject(new Error('ECONNREFUSED'));
      }) as unknown as typeof fetch;

      const result = await waitForPortFree(41777, 5000);

      expect(result).toBe(true);
      expect(callCount).toBeGreaterThanOrEqual(3);
    });

    it('should use default timeout when not specified', async () => {
      global.fetch = mock(() => Promise.reject(new Error('ECONNREFUSED'))) as unknown as typeof fetch;

      const result = await waitForPortFree(39999);

      expect(result).toBe(true);
    });
  });
});
