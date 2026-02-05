/**
 * MetricsService
 *
 * Collects and exposes metrics for observability.
 * Supports both JSON and Prometheus formats.
 */

import { DatabaseManager } from './DatabaseManager.js';
import { SessionManager } from './SessionManager.js';

export interface Metrics {
  uptime: number;
  memoryUsage: {
    heapUsed: number;
    heapTotal: number;
    rss: number;
    external: number;
  };
  database: {
    observations: number;
    sessions: number;
    summaries: number;
    prompts: number;
    sizeBytes: number;
  };
  processing: {
    activeSessions: number;
    queueDepth: number;
    isProcessing: boolean;
  };
  requests: {
    total: number;
    byEndpoint: Record<string, number>;
    errors: number;
    avgResponseTimeMs: number;
  };
  provider: {
    name: string;
    requestsTotal: number;
    tokensTotal: number;
    errorsTotal: number;
  };
  rates: {
    observationsPerMinute: number;
    requestsPerMinute: number;
  };
}

interface RequestMetric {
  endpoint: string;
  responseTimeMs: number;
  timestamp: number;
  error: boolean;
}

export class MetricsService {
  private dbManager: DatabaseManager;
  private sessionManager: SessionManager;
  private startTime: number;

  private requestMetrics: RequestMetric[] = [];
  private providerRequests: number = 0;
  private providerTokens: number = 0;
  private providerErrors: number = 0;
  private providerName: string = 'unknown';

  private readonly METRICS_WINDOW_MS = 5 * 60 * 1000;

  constructor(dbManager: DatabaseManager, sessionManager: SessionManager, startTime: number) {
    this.dbManager = dbManager;
    this.sessionManager = sessionManager;
    this.startTime = startTime;

    setInterval(() => this.cleanupOldMetrics(), 60000);
  }

  /**
   * Record a request metric
   */
  recordRequest(endpoint: string, responseTimeMs: number, error: boolean = false): void {
    this.requestMetrics.push({
      endpoint,
      responseTimeMs,
      timestamp: Date.now(),
      error,
    });
  }

  /**
   * Record provider usage
   */
  recordProviderUsage(provider: string, tokens: number, error: boolean = false): void {
    this.providerName = provider;
    this.providerRequests++;
    this.providerTokens += tokens;
    if (error) this.providerErrors++;
  }

  /**
   * Cleanup old metrics outside the window
   */
  private cleanupOldMetrics(): void {
    const cutoff = Date.now() - this.METRICS_WINDOW_MS;
    this.requestMetrics = this.requestMetrics.filter(m => m.timestamp > cutoff);
  }

  /**
   * Get all metrics
   */
  async getMetrics(): Promise<Metrics> {
    const store = this.dbManager.getSessionStore();
    const db = store.db;

    const safeCount = (table: string): number => {
      try {
        return (db.prepare(`SELECT COUNT(*) as count FROM ${table}`).get() as { count: number }).count;
      } catch {
        return 0;
      }
    };

    const obsCount = safeCount('observations');
    const sessCount = safeCount('sdk_sessions');
    const sumCount = safeCount('session_summaries');
    const promptCount = safeCount('prompts');

    const { DATA_DIR } = await import('../../shared/paths.js');
    const fs = await import('fs');
    const path = await import('path');
    const dbPath = path.join(DATA_DIR, 'pilot-memory.db');
    let dbSize = 0;
    try {
      const stat = fs.statSync(dbPath);
      dbSize = stat.size;
    } catch {
    }

    const memUsage = process.memoryUsage();

    const recentRequests = this.requestMetrics.filter(m => m.timestamp > Date.now() - this.METRICS_WINDOW_MS);
    const totalRequests = recentRequests.length;
    const errorRequests = recentRequests.filter(m => m.error).length;
    const avgResponseTime = totalRequests > 0
      ? recentRequests.reduce((sum, m) => sum + m.responseTimeMs, 0) / totalRequests
      : 0;

    const byEndpoint: Record<string, number> = {};
    for (const m of recentRequests) {
      byEndpoint[m.endpoint] = (byEndpoint[m.endpoint] || 0) + 1;
    }

    const oneMinuteAgo = Date.now() - 60000;
    let recentObs = 0;
    try {
      recentObs = (db.prepare('SELECT COUNT(*) as count FROM observations WHERE created_at_epoch > ?').get(oneMinuteAgo) as { count: number }).count;
    } catch {
    }
    const recentReqs = recentRequests.filter(m => m.timestamp > oneMinuteAgo).length;

    const isProcessing = this.sessionManager.isAnySessionProcessing();
    const queueDepth = this.sessionManager.getTotalActiveWork();
    const activeSessions = this.sessionManager.getActiveSessionCount();

    return {
      uptime: Math.floor((Date.now() - this.startTime) / 1000),
      memoryUsage: {
        heapUsed: memUsage.heapUsed,
        heapTotal: memUsage.heapTotal,
        rss: memUsage.rss,
        external: memUsage.external,
      },
      database: {
        observations: obsCount,
        sessions: sessCount,
        summaries: sumCount,
        prompts: promptCount,
        sizeBytes: dbSize,
      },
      processing: {
        activeSessions,
        queueDepth,
        isProcessing,
      },
      requests: {
        total: totalRequests,
        byEndpoint,
        errors: errorRequests,
        avgResponseTimeMs: Math.round(avgResponseTime),
      },
      provider: {
        name: this.providerName,
        requestsTotal: this.providerRequests,
        tokensTotal: this.providerTokens,
        errorsTotal: this.providerErrors,
      },
      rates: {
        observationsPerMinute: recentObs,
        requestsPerMinute: recentReqs,
      },
    };
  }

  /**
   * Format metrics as Prometheus text format
   */
  async toPrometheus(): Promise<string> {
    const metrics = await this.getMetrics();
    const lines: string[] = [];

    const addMetric = (name: string, value: number, help: string, type: string = 'gauge', labels: Record<string, string> = {}) => {
      lines.push(`# HELP claude_pilot_${name} ${help}`);
      lines.push(`# TYPE claude_pilot_${name} ${type}`);
      const labelStr = Object.entries(labels).map(([k, v]) => `${k}="${v}"`).join(',');
      const labelPart = labelStr ? `{${labelStr}}` : '';
      lines.push(`claude_pilot_${name}${labelPart} ${value}`);
    };

    addMetric('uptime_seconds', metrics.uptime, 'Worker uptime in seconds');
    addMetric('memory_heap_used_bytes', metrics.memoryUsage.heapUsed, 'Heap memory used');
    addMetric('memory_heap_total_bytes', metrics.memoryUsage.heapTotal, 'Total heap memory');
    addMetric('memory_rss_bytes', metrics.memoryUsage.rss, 'Resident set size');

    addMetric('database_observations_total', metrics.database.observations, 'Total observations');
    addMetric('database_sessions_total', metrics.database.sessions, 'Total sessions');
    addMetric('database_summaries_total', metrics.database.summaries, 'Total summaries');
    addMetric('database_prompts_total', metrics.database.prompts, 'Total prompts');
    addMetric('database_size_bytes', metrics.database.sizeBytes, 'Database file size');

    addMetric('processing_active_sessions', metrics.processing.activeSessions, 'Active processing sessions');
    addMetric('processing_queue_depth', metrics.processing.queueDepth, 'Queue depth');
    addMetric('processing_is_active', metrics.processing.isProcessing ? 1 : 0, 'Is processing active');

    addMetric('requests_total', metrics.requests.total, 'Total requests in window', 'counter');
    addMetric('requests_errors_total', metrics.requests.errors, 'Total request errors', 'counter');
    addMetric('requests_response_time_avg_ms', metrics.requests.avgResponseTimeMs, 'Average response time');

    addMetric('provider_requests_total', metrics.provider.requestsTotal, 'Provider requests', 'counter', { provider: metrics.provider.name });
    addMetric('provider_tokens_total', metrics.provider.tokensTotal, 'Provider tokens used', 'counter', { provider: metrics.provider.name });
    addMetric('provider_errors_total', metrics.provider.errorsTotal, 'Provider errors', 'counter', { provider: metrics.provider.name });

    addMetric('observations_per_minute', metrics.rates.observationsPerMinute, 'Observations created per minute');
    addMetric('requests_per_minute', metrics.rates.requestsPerMinute, 'Requests per minute');

    return lines.join('\n');
  }
}
