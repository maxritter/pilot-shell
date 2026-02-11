/**
 * Tests for Task 6: Expand StatsGrid with spec and session metrics
 *
 * Validates:
 * - StatsGrid accepts specStats and sessions props
 * - Renders Total Specs, Verified, In Progress, Sessions cards
 * - Uses renderToString to verify actual rendering
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";
import React from "react";
import { renderToString } from "react-dom/server";

const GRID_PATH = path.join(
  __dirname,
  "../../src/ui/viewer/views/Dashboard/StatsGrid.tsx",
);
const gridSource = readFileSync(GRID_PATH, "utf-8");

describe("Task 6: StatsGrid props", () => {
  it("should accept specStats prop in StatsGridProps", () => {
    expect(gridSource).toContain("specStats");
  });

  it("should accept sessions prop or use stats.sessions", () => {
    expect(gridSource).toMatch(/sessions/);
  });
});

describe("Task 6: StatsGrid renders spec cards", () => {
  it("should render Total Specs card", () => {
    expect(gridSource).toContain("Total Specs");
  });

  it("should render Verified card", () => {
    expect(gridSource).toContain("Verified");
  });

  it("should render In Progress card", () => {
    expect(gridSource).toContain("In Progress");
  });

  it("should render Sessions card", () => {
    expect(gridSource).toContain("Sessions");
  });

  it("should use correct icons for spec cards", () => {
    expect(gridSource).toContain("lucide:scroll");
    expect(gridSource).toContain("lucide:shield-check");
    expect(gridSource).toContain("lucide:loader");
    expect(gridSource).toContain("lucide:history");
  });
});

describe("Task 6: StatsGrid rendering", () => {
  it("should render all cards using renderToString", async () => {
    const { StatsGrid } = await import(
      "../../src/ui/viewer/views/Dashboard/StatsGrid"
    );
    const html = renderToString(
      React.createElement(StatsGrid, {
        stats: {
          observations: 100,
          summaries: 10,
          sessions: 25,
          lastObservationAt: "2h ago",
          projects: 3,
        },
        specStats: {
          totalSpecs: 14,
          verified: 10,
          inProgress: 2,
          pending: 2,
          avgIterations: 1.2,
          totalTasksCompleted: 45,
          totalTasks: 52,
          completionTimeline: [],
          recentlyVerified: [],
        },
      }),
    );
    expect(html).toContain("100");
    expect(html).toContain("14");
    expect(html).toContain("10");
    expect(html).toContain("25");
    expect(html).toContain("Observations");
    expect(html).toContain("Total Specs");
    expect(html).toContain("Verified");
    expect(html).toContain("Sessions");
  });
});
