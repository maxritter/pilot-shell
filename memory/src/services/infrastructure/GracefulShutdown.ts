/**
 * GracefulShutdown - Cleanup utilities for graceful exit
 *
 * Extracted from worker-service.ts to provide centralized shutdown coordination.
 * Handles:
 * - HTTP server closure (with Windows-specific delays)
 * - Session manager shutdown coordination
 * - Child process cleanup (Windows zombie port fix)
 */

import http from 'http';
import { logger } from '../../utils/logger.js';
import {
  getChildProcesses,
  forceKillProcess,
  waitForProcessesExit,
  removePidFile
} from './ProcessManager.js';

/** Timeout for each shutdown step (ms) */
const SHUTDOWN_STEP_TIMEOUT_MS = 5000;

/**
 * Run an async operation with a timeout. Returns true if completed, false if timed out.
 */
async function withTimeout<T>(
  operation: Promise<T>,
  timeoutMs: number,
  operationName: string
): Promise<{ completed: boolean; result?: T }> {
  const timeoutPromise = new Promise<{ completed: false }>((resolve) =>
    setTimeout(() => {
      logger.warn('SYSTEM', `${operationName} timed out after ${timeoutMs}ms`);
      resolve({ completed: false });
    }, timeoutMs)
  );

  const resultPromise = operation.then(result => ({ completed: true as const, result }));
  return Promise.race([resultPromise, timeoutPromise]);
}

export interface ShutdownableService {
  shutdownAll(): Promise<void>;
}

export interface CloseableClient {
  close(): Promise<void>;
}

export interface CloseableDatabase {
  close(): Promise<void>;
}

/**
 * Configuration for graceful shutdown
 */
export interface GracefulShutdownConfig {
  server: http.Server | null;
  sessionManager: ShutdownableService;
  mcpClient?: CloseableClient;
  dbManager?: CloseableDatabase;
}

/**
 * Perform graceful shutdown of all services
 *
 * IMPORTANT: On Windows, we must kill all child processes before exiting
 * to prevent zombie ports. The socket handle can be inherited by children,
 * and if not properly closed, the port stays bound after process death.
 */
export async function performGracefulShutdown(config: GracefulShutdownConfig): Promise<void> {
  logger.info('SYSTEM', 'Shutdown initiated');

  removePidFile();

  const childPidsResult = await withTimeout(
    getChildProcesses(process.pid),
    SHUTDOWN_STEP_TIMEOUT_MS,
    'Enumerate child processes'
  );
  const childPids = childPidsResult.completed ? (childPidsResult.result ?? []) : [];
  logger.info('SYSTEM', 'Found child processes', { count: childPids.length, pids: childPids });

  if (config.server) {
    await withTimeout(
      closeHttpServer(config.server),
      SHUTDOWN_STEP_TIMEOUT_MS,
      'Close HTTP server'
    );
    logger.info('SYSTEM', 'HTTP server closed');
  }

  await withTimeout(
    config.sessionManager.shutdownAll(),
    SHUTDOWN_STEP_TIMEOUT_MS,
    'Shutdown sessions'
  );

  if (config.mcpClient) {
    await withTimeout(
      config.mcpClient.close(),
      SHUTDOWN_STEP_TIMEOUT_MS,
      'Close MCP client'
    );
    logger.info('SYSTEM', 'MCP client closed');
  }

  if (config.dbManager) {
    await withTimeout(
      config.dbManager.close(),
      SHUTDOWN_STEP_TIMEOUT_MS,
      'Close database'
    );
  }

  if (childPids.length > 0) {
    logger.info('SYSTEM', 'Force killing remaining children');
    for (const pid of childPids) {
      await forceKillProcess(pid);
    }
    await waitForProcessesExit(childPids, 5000);
  }

  logger.info('SYSTEM', 'Worker shutdown complete');
}

/**
 * Close HTTP server with Windows-specific delays
 * Windows needs extra time to release sockets properly
 */
async function closeHttpServer(server: http.Server): Promise<void> {
  server.closeAllConnections();

  if (process.platform === 'win32') {
    await new Promise(r => setTimeout(r, 500));
  }

  await new Promise<void>((resolve, reject) => {
    server.close(err => err ? reject(err) : resolve());
  });

  if (process.platform === 'win32') {
    await new Promise(r => setTimeout(r, 500));
    logger.info('SYSTEM', 'Waited for Windows port cleanup');
  }
}
