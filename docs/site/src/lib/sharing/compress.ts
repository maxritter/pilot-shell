/**
 * Deflate-raw compression with base64url encoding for URL-safe sharing.
 *
 * Uses CompressionStream('deflate-raw') — available in Chrome 80+, Firefox 113+, Safari 16.4+.
 * Uses Uint8Array.toBase64/fromBase64 (Chrome 128+, Safari 17.4+, Firefox 133+).
 */

export async function compress(data: string): Promise<string> {
  const byteArray = new TextEncoder().encode(data);
  const stream = new CompressionStream("deflate-raw");
  const writer = stream.writable.getWriter();
  writer.write(byteArray);
  writer.close();
  const buffer = await new Response(stream.readable).arrayBuffer();
  return new Uint8Array(buffer).toBase64({ alphabet: "base64url", omitPadding: true });
}

export async function decompress(b64: string): Promise<string> {
  // Uint8Array.fromBase64 is typed as Uint8Array<ArrayBufferLike> which TS 5.7+
  // refuses to pass to writer.write(BufferSource) because ArrayBufferLike includes
  // SharedArrayBuffer. Copy into a fresh ArrayBuffer-backed view to satisfy the type.
  const decoded = Uint8Array.fromBase64(b64, { alphabet: "base64url" });
  const byteArray = new Uint8Array(decoded.byteLength);
  byteArray.set(decoded);
  const stream = new DecompressionStream("deflate-raw");
  const writer = stream.writable.getWriter();
  writer.write(byteArray);
  writer.close();
  const buffer = await new Response(stream.readable).arrayBuffer();
  return new TextDecoder().decode(buffer);
}
