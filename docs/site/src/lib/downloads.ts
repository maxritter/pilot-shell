import { isPhone } from "@/lib/device";

/** What the download page knows about the newest release and the visitor. */

/** What /app/downloads.json says about the newest release: its packages with address and size in bytes. */
export type Packages = { version: string; packages: { id: string; name: string; url: string; size: number }[] };

export type Card = "macos-arm64" | "macos-x64" | "windows" | "linux";

/** The visitor's system from the browser's own words; a phone has no card, and Android's Linux is not Linux's. */
export function systemOf(userAgent: string, arch?: string): Card | null {
  if (isPhone(userAgent)) return null;
  if (/Windows/.test(userAgent)) return "windows";
  if (/Macintosh|Mac OS X/.test(userAgent)) return arch === "x86" ? "macos-x64" : "macos-arm64";
  if (/Linux|X11/.test(userAgent)) return "linux";
  return null;
}

export const sizeLabel = (bytes: number) => `${Math.round(bytes / 1_000_000)} MB`;

/** The release's packages, or null when there is none yet or GitHub cannot say; the page then points at the releases page. */
export async function loadPackages(fetchFn: typeof fetch = fetch): Promise<Packages | null> {
  try {
    const response = await fetchFn("/app/downloads.json");
    return response.ok ? ((await response.json()) as Packages) : null;
  } catch {
    return null;
  }
}
