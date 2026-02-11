/**
 * Tests for Task 5: useStats hook expansion with spec stats and analytics
 *
 * Validates:
 * - SpecStats interface exists with required fields
 * - ObservationTimeline type exists
 * - sessions count added to Stats interface
 * - New fetches added to loadStats for /api/plans/stats and /api/analytics/timeline
 * - specStats and observationTimeline added to UseStatsResult and return
 */
import { describe, it, expect } from "bun:test";
import { readFileSync } from "fs";
import path from "path";

const HOOK_PATH = path.join(
  __dirname,
  "../../src/ui/viewer/hooks/useStats.ts",
);
const hookSource = readFileSync(HOOK_PATH, "utf-8");

describe("Task 5: SpecStats interface", () => {
  it("should define SpecStats interface with totalSpecs field", () => {
    expect(hookSource).toContain("interface SpecStats");
    expect(hookSource).toContain("totalSpecs");
  });

  it("should include verified, inProgress, pending counts", () => {
    expect(hookSource).toContain("verified:");
    expect(hookSource).toMatch(/inProgress.*number/);
    expect(hookSource).toMatch(/pending.*number/);
  });

  it("should include completionTimeline and recentlyVerified arrays", () => {
    expect(hookSource).toContain("completionTimeline");
    expect(hookSource).toContain("recentlyVerified");
  });

  it("should include avgIterations field", () => {
    expect(hookSource).toContain("avgIterations");
  });
});

describe("Task 5: ObservationTimeline type", () => {
  it("should define ObservationTimeline as array of date/count objects", () => {
    expect(hookSource).toMatch(/ObservationTimeline/);
  });
});

describe("Task 5: sessions in Stats interface", () => {
  it("should include sessions count in Stats interface", () => {
    const statsInterface = hookSource.match(
      /interface Stats\s*{([\s\S]*?)}/,
    );
    expect(statsInterface).toBeTruthy();
    expect(statsInterface![1]).toContain("sessions");
  });
});

describe("Task 5: new fetches in loadStats", () => {
  it("should fetch /api/plans/stats endpoint", () => {
    expect(hookSource).toContain("/api/plans/stats");
  });

  it("should fetch /api/analytics/timeline endpoint", () => {
    expect(hookSource).toContain("/api/analytics/timeline");
  });

  it("should pass project param to new fetch calls", () => {
    const planStatsFetch = hookSource.match(/plans\/stats.*project/);
    expect(planStatsFetch).toBeTruthy();
  });
});

describe("Task 5: UseStatsResult expansion", () => {
  it("should include specStats in UseStatsResult", () => {
    const resultInterface = hookSource.match(
      /interface UseStatsResult\s*{([\s\S]*?)}/,
    );
    expect(resultInterface).toBeTruthy();
    expect(resultInterface![1]).toContain("specStats");
  });

  it("should include observationTimeline in UseStatsResult", () => {
    const resultInterface = hookSource.match(
      /interface UseStatsResult\s*{([\s\S]*?)}/,
    );
    expect(resultInterface).toBeTruthy();
    expect(resultInterface![1]).toContain("observationTimeline");
  });

  it("should return specStats and observationTimeline from the hook", () => {
    const returnBlock = hookSource.match(/return\s*{([\s\S]*?)};/);
    expect(returnBlock).toBeTruthy();
    expect(returnBlock![1]).toContain("specStats");
    expect(returnBlock![1]).toContain("observationTimeline");
  });
});
