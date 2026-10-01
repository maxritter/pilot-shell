import { describe, expect, it, vi } from "vitest";
import { loadShare } from "./sharing";

/** The share page reads v2 links only; Pilot Shell 11's compressed specs are no longer served. */

const answer = (status: number, body?: unknown) =>
  vi.fn(async () => new Response(body === undefined ? null : JSON.stringify(body), { status })) as unknown as typeof fetch;

/** A Pilot Shell 11 payload the way it stored it: deflate-raw, then base64url. */
async function v11Data(text: string): Promise<string> {
  const stream = new Blob([text]).stream().pipeThrough(new CompressionStream("deflate-raw"));
  const bytes = new Uint8Array(await new Response(stream).arrayBuffer());
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

describe("loading a link", () => {
  it("does not read a valid compressed Pilot Shell 11 spec", async () => {
    const data = await v11Data(JSON.stringify({ specContent: "# Old spec", annotations: [], createdAt: 1 }));
    const loaded = await loadShare("A".repeat(22), answer(200, { data }));
    expect(loaded.status).toBe("error");
  });

  it("does not take an 8-character id for a link", async () => {
    const never = answer(200, {});
    expect((await loadShare("ABCD1234", never)).status).toBe("error");
    expect(never).not.toHaveBeenCalled();
  });
});
