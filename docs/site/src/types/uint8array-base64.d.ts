// Ambient declarations for the Uint8Array base64 API (TC39 Stage 3).
// Shipped in Chrome 128+, Safari 17.4+, Firefox 133+ but not yet in TypeScript's
// bundled lib.es*.d.ts. Remove this file once TypeScript's lib includes them.
//
// Spec: https://tc39.es/proposal-arraybuffer-base64/

interface Uint8ArrayBase64Options {
  alphabet?: "base64" | "base64url";
  omitPadding?: boolean;
}

interface Uint8ArrayFromBase64Options {
  alphabet?: "base64" | "base64url";
  lastChunkHandling?: "loose" | "strict" | "stop-before-partial";
}

interface Uint8Array {
  toBase64(options?: Uint8ArrayBase64Options): string;
  toHex(): string;
}

interface Uint8ArrayConstructor {
  fromBase64(input: string, options?: Uint8ArrayFromBase64Options): Uint8Array;
  fromHex(input: string): Uint8Array;
}
