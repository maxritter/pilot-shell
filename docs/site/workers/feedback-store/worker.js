// The only way into the private bucket that holds feedback screenshots. qualitylayer.dev's API
// holds STORE_SECRET and nothing else, so no R2 access keys exist anywhere. The bucket is bound
// here as BUCKET (see wrangler.jsonc); STORE_SECRET is set with `wrangler secret put`.
//
//   PUT /o/<key>   stores the body under its content-type
//   GET /o/<key>   returns it
//
// A key is exactly what api/feedback writes: feedback/<yyyymmdd>/<32 hex>/<1-5>.<png|jpg|webp>.

const KEY = /^feedback\/(\d{8})\/[0-9a-f]{32}\/[1-5]\.(png|jpg|webp)$/;
const TYPES = { png: "image/png", jpg: "image/jpeg", webp: "image/webp" };
const MAX_BYTES = 5 * 1024 * 1024;
const DAY_MS = 24 * 60 * 60 * 1000;
// Links last 90 days from the report's own day; the key's day counts to its end.
const KEEP_MS = 91 * DAY_MS;

const text = (status, body) => new Response(body, { status, headers: { "Content-Type": "text/plain" } });

/** True when both digests match; compares them whole, whatever their length, so timing says nothing. */
async function sameSecret(given, expected) {
  const digest = async (value) => new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)));
  const [a, b] = await Promise.all([digest(given), digest(expected)]);
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}

/** The key's day as a time, or null when it is not a real date. */
function dayOf(digits) {
  const year = Number(digits.slice(0, 4));
  const month = Number(digits.slice(4, 6));
  const day = Number(digits.slice(6, 8));
  const time = Date.UTC(year, month - 1, day);
  const back = new Date(time);
  return back.getUTCFullYear() === year && back.getUTCMonth() === month - 1 && back.getUTCDate() === day ? time : null;
}

export default {
  async fetch(request, env) {
    const secret = env.STORE_SECRET;
    const bearer = /^Bearer (.+)$/.exec(request.headers.get("Authorization") ?? "");
    if (!secret || !bearer || !(await sameSecret(bearer[1], secret))) return text(401, "unauthorised");

    if (request.method !== "GET" && request.method !== "PUT") return text(405, "method not allowed");

    const path = new URL(request.url).pathname;
    const key = path.startsWith("/o/") ? path.slice(3) : "";
    const match = KEY.exec(key);
    const day = match ? dayOf(match[1]) : null;
    // A key past its 90 days is as good as gone, whatever the bucket still holds.
    if (!match || day === null || Date.now() >= day + KEEP_MS) return text(404, "not found");

    if (request.method === "GET") {
      const object = await env.BUCKET.get(key);
      if (object === null) return text(404, "not found");
      return new Response(object.body, {
        headers: { "Content-Type": object.httpMetadata?.contentType ?? TYPES[match[2]], "Cache-Control": "private, no-store" },
      });
    }

    const type = (request.headers.get("Content-Type") ?? "").split(";")[0].trim().toLowerCase();
    if (type !== TYPES[match[2]]) return text(400, "the content type must match the key");
    if (Number(request.headers.get("Content-Length") ?? 0) > MAX_BYTES) return text(413, "too large");
    const body = await request.arrayBuffer();
    if (body.byteLength > MAX_BYTES) return text(413, "too large");
    await env.BUCKET.put(key, body, { httpMetadata: { contentType: type } });
    return text(200, "stored");
  },
};
