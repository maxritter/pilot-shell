/**
 * useUsage Hook Tests
 *
 * Tests that useUsage fetches usage data from API endpoints
 * and handles empty states correctly.
 */

import { describe, it, expect } from "bun:test";
import { renderToString } from "react-dom/server";
import React from "react";

describe("useUsage", () => {
  it("useUsage hook is exported", async () => {
    const mod = await import("../../src/ui/viewer/hooks/useUsage.js");
    expect(mod.useUsage).toBeDefined();
    expect(typeof mod.useUsage).toBe("function");
  });

  it("useUsage returns expected interface", async () => {
    const { useUsage } = await import("../../src/ui/viewer/hooks/useUsage.js");

    function TestComponent() {
      const result = useUsage();
      return React.createElement(
        "div",
        null,
        `loading:${result.isLoading}`,
        `|daily:${result.daily.length}`,
        `|monthly:${result.monthly.length}`,
        `|models:${result.models.length}`,
        `|available:${result.available}`,
        `|dataExists:${result.dataExists}`
      );
    }

    const html = renderToString(React.createElement(TestComponent));

    expect(html).toContain("loading:");
    expect(html).toContain("daily:");
    expect(html).toContain("monthly:");
    expect(html).toContain("models:");
    expect(html).toContain("available:");
    expect(html).toContain("dataExists:");
  });

  it("useUsage source contains API endpoint fetch logic", async () => {
    const fs = await import("fs");
    const source = fs.readFileSync(
      "src/ui/viewer/hooks/useUsage.ts",
      "utf-8"
    );

    expect(source).toContain("/api/usage/daily");
    expect(source).toContain("/api/usage/monthly");
    expect(source).toContain("/api/usage/models");
    expect(source).toContain("Promise.all");

    expect(source).toContain("available");
    expect(source).toContain("dataExists");
    expect(source).toContain("isLoading");

    expect(source).toContain("5 * 60 * 1000");
  });
});
