import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./compress", () => ({
  compress: vi.fn(async (s: string) => `compressed:${s.length}`),
  decompress: vi.fn(async (s: string) => s),
}));

import { generateShortFeedbackUrl } from "./sharing";
import type { FeedbackPayload } from "./types";

const samplePayload: FeedbackPayload = {
  annotations: [],
  author: "Tester",
  planPath: "docs/plans/x.md",
  createdAt: 0,
};

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("generateShortFeedbackUrl", () => {
  it("returns short URL on 201", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ id: "ABCDEFGH" }), { status: 201 }),
    );
    const result = await generateShortFeedbackUrl(samplePayload, "");
    expect(result).toEqual({
      ok: true,
      url: "https://pilot-shell.com/s/ABCDEFGH",
    });
  });

  it("returns too_large on 413", async () => {
    fetchMock.mockResolvedValueOnce(new Response("", { status: 413 }));
    const result = await generateShortFeedbackUrl(samplePayload, "");
    expect(result).toEqual({ ok: false, reason: "too_large" });
  });

  it("returns rate_limited on 429", async () => {
    fetchMock.mockResolvedValueOnce(new Response("", { status: 429 }));
    const result = await generateShortFeedbackUrl(samplePayload, "");
    expect(result).toEqual({ ok: false, reason: "rate_limited" });
  });

  it("returns network on fetch rejection", async () => {
    fetchMock.mockRejectedValueOnce(new Error("offline"));
    const result = await generateShortFeedbackUrl(samplePayload, "");
    expect(result).toEqual({ ok: false, reason: "network" });
  });

  it("returns network on malformed response id", async () => {
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ id: "" }), { status: 201 }),
    );
    const result = await generateShortFeedbackUrl(samplePayload, "");
    expect(result).toEqual({ ok: false, reason: "network" });
  });
});
