/**
 * AES-256-GCM encryption for zero-knowledge URL sharing.
 *
 * Uses Web Crypto API — works in all modern browsers.
 * The encryption key never leaves the client; it lives in the URL fragment
 * as a query param (?key=<base64url>), which the HTTP spec guarantees
 * is never sent to the server.
 *
 * Ciphertext format: base64url(12-byte IV || GCM ciphertext+tag)
 */

export async function encrypt(
  plaintext: string,
): Promise<{ ciphertext: string; key: string }> {
  const cryptoKey = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt"],
  );

  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encoded = new TextEncoder().encode(plaintext);

  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    cryptoKey,
    encoded,
  );

  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(encrypted), iv.length);

  const rawKey = await crypto.subtle.exportKey("raw", cryptoKey);

  return {
    ciphertext: combined.toBase64({ alphabet: "base64url", omitPadding: true }),
    key: new Uint8Array(rawKey).toBase64({ alphabet: "base64url", omitPadding: true }),
  };
}

export async function decrypt(ciphertext: string, key: string): Promise<string> {
  const combined = Uint8Array.fromBase64(ciphertext, { alphabet: "base64url" });
  const rawKey = Uint8Array.fromBase64(key, { alphabet: "base64url" });

  const iv = combined.slice(0, 12);
  const encrypted = combined.slice(12);

  const cryptoKey = await crypto.subtle.importKey(
    "raw",
    rawKey.buffer as ArrayBuffer,
    { name: "AES-GCM", length: 256 },
    false,
    ["decrypt"],
  );

  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    cryptoKey,
    encrypted,
  );

  return new TextDecoder().decode(decrypted);
}
