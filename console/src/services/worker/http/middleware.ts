/**
 * HTTP Middleware for Worker Service
 *
 * Extracted from WorkerService.ts for better organization.
 * Handles request/response logging, CORS, JSON parsing, and static file serving.
 */

import express, { Request, Response, NextFunction, RequestHandler } from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import path from "path";
import { getPackageRoot } from "../../../shared/paths.js";
import { logger } from "../../../utils/logger.js";

const LOCALHOST_PATTERNS = [
  /^https?:\/\/localhost(:\d+)?$/,
  /^https?:\/\/127\.0\.0\.1(:\d+)?$/,
  /^https?:\/\/\[::1\](:\d+)?$/,
];

/** Check if an origin is a localhost address (or undefined for non-browser clients). */
export function isAllowedOrigin(origin: string | undefined): boolean {
  if (origin === undefined) return true;
  return LOCALHOST_PATTERNS.some((pattern) => pattern.test(origin));
}

/**
 * Create all middleware for the worker service
 * @param summarizeRequestBody - Function to summarize request bodies for logging
 * @returns Array of middleware functions
 */
export function createMiddleware(
  summarizeRequestBody: (method: string, path: string, body: any) => string,
): RequestHandler[] {
  const middlewares: RequestHandler[] = [];

  middlewares.push(express.json({ limit: "50mb" }));

  middlewares.push(
    cors({
      origin: (origin, callback) => {
        if (isAllowedOrigin(origin)) {
          callback(null, true);
        } else {
          logger.warn("SECURITY", "CORS request blocked", { origin });
          callback(null, false);
        }
      },
    }),
  );

  middlewares.push(cookieParser());

  middlewares.push((req: Request, res: Response, next: NextFunction) => {
    const staticExtensions = [
      ".html",
      ".js",
      ".css",
      ".svg",
      ".png",
      ".jpg",
      ".jpeg",
      ".webp",
      ".woff",
      ".woff2",
      ".ttf",
      ".eot",
    ];
    const isStaticAsset = staticExtensions.some((ext) => req.path.endsWith(ext));
    const isPollingEndpoint = req.path === "/api/logs";
    if (req.path.startsWith("/health") || req.path === "/" || isStaticAsset || isPollingEndpoint) {
      return next();
    }

    const start = Date.now();
    const requestId = `${req.method}-${Date.now()}`;

    const bodySummary = summarizeRequestBody(req.method, req.path, req.body);
    logger.info("HTTP", `→ ${req.method} ${req.path}`, { requestId }, bodySummary);

    const originalSend = res.send.bind(res);
    res.send = function (body: any) {
      const duration = Date.now() - start;
      logger.info("HTTP", `← ${res.statusCode} ${req.path}`, { requestId, duration: `${duration}ms` });
      return originalSend(body);
    };

    next();
  });

  const packageRoot = getPackageRoot();
  const uiDir = path.join(packageRoot, "plugin", "ui");
  middlewares.push(express.static(uiDir));

  return middlewares;
}

/**
 * Middleware to require localhost-only access
 * Used for admin endpoints that should not be exposed when binding to 0.0.0.0
 */
export function requireLocalhost(req: Request, res: Response, next: NextFunction): void {
  const clientIp = req.ip || req.connection.remoteAddress || "";
  const isLocalhost =
    clientIp === "127.0.0.1" || clientIp === "::1" || clientIp === "::ffff:127.0.0.1" || clientIp === "localhost";

  if (!isLocalhost) {
    logger.warn("SECURITY", "Admin endpoint access denied - not localhost", {
      endpoint: req.path,
      clientIp,
      method: req.method,
    });
    res.status(403).json({
      error: "Forbidden",
      message: "Admin endpoints are only accessible from localhost",
    });
    return;
  }

  next();
}

/**
 * Summarize request body for logging
 * Used to avoid logging sensitive data or large payloads
 */
export function summarizeRequestBody(method: string, path: string, body: any): string {
  if (!body || Object.keys(body).length === 0) return "";

  if (path.includes("/init")) {
    return "";
  }

  if (path.includes("/observations")) {
    const toolName = body.tool_name || "?";
    const toolInput = body.tool_input;
    const toolSummary = logger.formatTool(toolName, toolInput);
    return `tool=${toolSummary}`;
  }

  if (path.includes("/summarize")) {
    return "requesting summary";
  }

  return "";
}
