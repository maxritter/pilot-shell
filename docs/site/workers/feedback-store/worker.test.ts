import { beforeEach, describe, expect, it } from "vitest";
// @ts-expect-error the Worker is plain JavaScript, bundled by wrangler
import worker from "./worker.js";

/**
 * The Worker is the only thing that touches the private bucket. The site's API holds a shared
 * secret and nothing else: no R2 access keys exist. A fake binding stands in for the bucket.
 */

const SECRET = "store-secret";
const DAY = 86_400_000;

type Stored = { bytes: Uint8Array<ArrayBuffer>; contentType: string | undefined };

class FakeBucket {
  objects = new Map<string, Stored>();
  async put(key: string, body: ArrayBuffer, options?: { httpMetadata?: { contentType?: string } }) {
    this.objects.set(key, { bytes: new Uint8Array(body), contentType: options?.httpMetadata?.contentType });
  }
  async get(key: string) {
    const found = this.objects.get(key);
    if (!found) return null;
    return { body: new Response(found.bytes).body, httpMetadata: { contentType: found.contentType } };
  }
}

const stamp = (ms: number) => new Date(ms).toISOString().slice(0, 10).replaceAll("-", "");
const keyOn = (ms: number, name = "1.png") => `feedback/${stamp(ms)}/0123456789abcdef0123456789abcdef/${name}`;
const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 1, 2, 3]);

let bucket: FakeBucket;
let env: { BUCKET: FakeBucket; STORE_SECRET?: string };

beforeEach(() => {
  bucket = new FakeBucket();
  env = { BUCKET: bucket, STORE_SECRET: SECRET };
});

const call = (method: string, path: string, init: { auth?: string | null; body?: BodyInit; type?: string } = {}) => {
  const headers: Record<string, string> = {};
  const auth = init.auth === undefined ? `Bearer ${SECRET}` : init.auth;
  if (auth !== null) headers.authorization = auth;
  if (init.type) headers["content-type"] = init.type;
  return worker.fetch(new Request(`https://store.example.workers.dev${path}`, { method, headers, body: init.body }), env) as Promise<Response>;
};

describe("feedback-store Worker", () => {
  it("stores a screenshot with its type and hands it back", async () => {
    const key = keyOn(Date.now());
    expect((await call("PUT", `/o/${key}`, { body: PNG, type: "image/png" })).status).toBe(200);
    expect(bucket.objects.get(key)?.contentType).toBe("image/png");
    const res = await call("GET", `/o/${key}`);
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("image/png");
    expect(new Uint8Array(await res.arrayBuffer())).toEqual(PNG);
  });

  it("answers 404 for a key that is not stored", async () => {
    expect((await call("GET", `/o/${keyOn(Date.now())}`)).status).toBe(404);
  });

  it("wants the shared secret on every request, before it says anything else", async () => {
    const key = keyOn(Date.now());
    await call("PUT", `/o/${key}`, { body: PNG, type: "image/png" });
    for (const auth of [null, "", "Bearer", "Bearer wrong", "Bearer store-secret-and-more", "Bearer store-secre", SECRET, "Basic c3RvcmUtc2VjcmV0"]) {
      expect((await call("GET", `/o/${key}`, { auth })).status).toBe(401);
      expect((await call("PUT", `/o/${key}`, { auth, body: PNG, type: "image/png" })).status).toBe(401);
    }
    expect((await call("GET", "/nothing", { auth: null })).status).toBe(401);
    expect(bucket.objects.size).toBe(1);
  });

  it("refuses everything while no secret is set", async () => {
    env.STORE_SECRET = undefined;
    expect((await call("GET", `/o/${keyOn(Date.now())}`, { auth: "Bearer " })).status).toBe(401);
    expect((await call("GET", `/o/${keyOn(Date.now())}`, { auth: "Bearer undefined" })).status).toBe(401);
  });

  it("serves only the keys the site writes", async () => {
    for (const bad of [
      "feedback/20261004/short/1.png",
      `feedback/${stamp(Date.now())}/0123456789abcdef0123456789abcdef/6.png`,
      `feedback/${stamp(Date.now())}/0123456789abcdef0123456789abcdef/1.svg`,
      `feedback/${stamp(Date.now())}/0123456789abcdef0123456789abcdef/1.png/extra`,
      `other/${stamp(Date.now())}/0123456789abcdef0123456789abcdef/1.png`,
      `feedback/${stamp(Date.now())}/../0123456789abcdef0123456789abcdef/1.png`,
    ]) {
      expect((await call("GET", `/o/${bad}`)).status).toBe(404);
      expect((await call("PUT", `/o/${bad}`, { body: PNG, type: "image/png" })).status).toBe(404);
    }
    expect((await call("GET", "/")).status).toBe(404);
    expect((await call("GET", "/o/")).status).toBe(404);
    expect(bucket.objects.size).toBe(0);
  });

  it("takes only GET and PUT", async () => {
    const path = `/o/${keyOn(Date.now())}`;
    for (const method of ["DELETE", "POST", "PATCH"]) {
      expect((await call(method, path, method === "DELETE" ? {} : { body: "x" })).status).toBe(405);
    }
  });

  it("stores only image types that match the key's extension", async () => {
    const path = `/o/${keyOn(Date.now())}`;
    expect((await call("PUT", path, { body: PNG, type: "text/html" })).status).toBe(400);
    expect((await call("PUT", path, { body: PNG, type: "image/jpeg" })).status).toBe(400);
    expect((await call("PUT", path, { body: PNG })).status).toBe(400);
    expect((await call("PUT", `/o/${keyOn(Date.now(), "2.jpg")}`, { body: PNG, type: "image/jpeg" })).status).toBe(200);
    expect((await call("PUT", `/o/${keyOn(Date.now(), "3.webp")}`, { body: PNG, type: "image/webp" })).status).toBe(200);
    expect(bucket.objects.size).toBe(2);
  });

  it("refuses an object over 5 MB", async () => {
    const big = new Uint8Array(5 * 1024 * 1024 + 1);
    expect((await call("PUT", `/o/${keyOn(Date.now())}`, { body: big, type: "image/png" })).status).toBe(413);
    expect(bucket.objects.size).toBe(0);
  });

  it("refuses a key older than 90 days by the date in it, and still serves one just inside", async () => {
    const old = keyOn(Date.now() - 95 * DAY);
    bucket.objects.set(old, { bytes: PNG, contentType: "image/png" });
    expect((await call("GET", `/o/${old}`)).status).toBe(404);
    expect((await call("PUT", `/o/${old}`, { body: PNG, type: "image/png" })).status).toBe(404);

    const inside = keyOn(Date.now() - 89 * DAY);
    bucket.objects.set(inside, { bytes: PNG, contentType: "image/png" });
    expect((await call("GET", `/o/${inside}`)).status).toBe(200);
  });

  it("refuses a date that is not a date", async () => {
    expect((await call("GET", "/o/feedback/20261340/0123456789abcdef0123456789abcdef/1.png")).status).toBe(404);
  });
});
