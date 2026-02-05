/**
 * Agent Consolidation Module
 *
 * This module provides shared utilities for the SDK agent.
 * It extracts common patterns to reduce code duplication and ensure consistent behavior.
 *
 * Usage:
 * ```typescript
 * import { processAgentResponse } from './agents/index.js';
 * ```
 */

export type {
  WorkerRef,
  ObservationSSEPayload,
  SummarySSEPayload,
  SSEEventPayload,
  StorageResult,
  ResponseProcessingContext,
  ParsedResponse,
  FallbackAgent,
  BaseAgentConfig,
} from './types.js';

export { FALLBACK_ERROR_PATTERNS } from './types.js';

export { processAgentResponse } from './ResponseProcessor.js';

export { broadcastObservation, broadcastSummary } from './ObservationBroadcaster.js';

export { cleanupProcessedMessages } from './SessionCleanupHelper.js';

export { shouldFallbackToClaude, isAbortError } from './FallbackErrorHandler.js';
