import { renderToReadableStream } from "react-dom/server.browser";
import { describe, expect, it, vi } from "vitest";
import { loadPackages, type Packages, sizeLabel, systemOf } from "@/lib/downloads";
import { DownloadView } from "./Download";

/**
 * The download page: a card per system with the visitor's own first and highlighted, each linking
 * to the package the release names and showing its size, and the command line for machines
 * without a screen. What the release holds comes from /app/downloads.json, nothing is hard-coded.
 */

const WINDOWS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36";
const MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15";
const LINUX = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36";
const ANDROID = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36";

const asset = (id: string, file: string, size: number) => ({ id, name: file, url: `https://github.com/maxritter/pilot-shell/releases/download/v12.0.0/${file}`, size });
const PACKAGES: Packages = {
  version: "12.0.0",
  packages: [
    asset("macos-arm64", "QualityLayer-12.0.0-macos-arm64.dmg", 84_300_000),
    asset("macos-x64", "QualityLayer-12.0.0-macos-x64.dmg", 88_100_000),
    asset("windows-x64", "QualityLayer-12.0.0-x64-setup.exe", 61_900_000),
    asset("windows-arm64", "QualityLayer-12.0.0-arm64-setup.exe", 58_400_000),
    asset("linux-x64", "QualityLayer-12.0.0-linux-x64.AppImage", 97_000_000),
    asset("linux-arm64", "QualityLayer-12.0.0-linux-arm64.AppImage", 95_200_000),
  ],
};

async function html(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(node);
  await stream.allReady;
  return new Response(stream).text();
}

/** The markup of the card holding this heading: from its opening tag to the next card's. */
const cardOf = (markup: string, heading: string) => {
  const cards = markup.split('<div class="ap-os"').slice(1);
  return cards.find((card) => card.includes(`<b>${heading}</b>`))!;
};

describe("which system a visitor is on", () => {
  it("picks the card from the browser: Windows, a Mac (Apple silicon unless the browser says Intel), Linux", () => {
    expect(systemOf(WINDOWS)).toBe("windows");
    expect(systemOf(MAC)).toBe("macos-arm64");
    expect(systemOf(MAC, "x86")).toBe("macos-x64");
    expect(systemOf(LINUX)).toBe("linux");
  });

  it("picks none for a phone, an Android phone's Linux included, and for what it does not know", () => {
    expect(systemOf(ANDROID)).toBeNull();
    expect(systemOf("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)")).toBeNull();
    expect(systemOf("curl/8.7.1")).toBeNull();
  });
});

describe("the cards", () => {
  it("highlights the Windows card for a Windows visitor, lists it first, and no other", async () => {
    const markup = await html(<DownloadView data={PACKAGES} system={systemOf(WINDOWS)} />);
    expect(markup.match(/data-current="true"/g)).toHaveLength(1);
    expect(cardOf(markup, "Windows")).toContain('data-current="true"');
    expect(markup.indexOf("<b>Windows</b>")).toBeLessThan(markup.indexOf("<b>Linux</b>"));
    expect(markup.indexOf("<b>Windows</b>")).toBeLessThan(markup.indexOf("<b>macOS</b>"));
  });

  it("links each card to the package the release names and shows its size", async () => {
    const markup = await html(<DownloadView data={PACKAGES} system={null} />);
    const windows = cardOf(markup, "Windows");
    expect(windows).toContain('href="https://github.com/maxritter/pilot-shell/releases/download/v12.0.0/QualityLayer-12.0.0-x64-setup.exe"');
    expect(windows).toContain("62 MB");
    expect(windows).toContain('href="https://github.com/maxritter/pilot-shell/releases/download/v12.0.0/QualityLayer-12.0.0-arm64-setup.exe"');
    expect(windows).toContain("58 MB");

    const linux = cardOf(markup, "Linux");
    expect(linux).toContain("QualityLayer-12.0.0-linux-x64.AppImage");
    expect(linux).toContain("97 MB");

    expect(markup).toContain("QualityLayer-12.0.0-macos-arm64.dmg");
    expect(markup).toContain("84 MB");
    expect(markup).toContain("QualityLayer-12.0.0-macos-x64.dmg");
    expect(markup).toContain("88 MB");
  });

  it("offers the command line for machines with no screen, with the install command", async () => {
    const markup = await html(<DownloadView data={PACKAGES} system={null} />);
    expect(markup).toContain("Command line only");
    expect(markup).toContain("curl -fsSL https://qualitylayer.dev/install.sh | bash");
  });

  it("says what Windows may show on a new app", async () => {
    const markup = await html(<DownloadView data={PACKAGES} system={null} />);
    expect(markup).toContain("SmartScreen");
    expect(markup).toContain("Run anyway");
  });

  it("still shows every card when the release list is unavailable, linking to the releases page with no size", async () => {
    const markup = await html(<DownloadView data={null} system="linux" />);
    expect(markup).toContain("<b>macOS</b>");
    expect(markup).toContain("<b>Windows</b>");
    expect(markup).toContain('href="https://github.com/maxritter/pilot-shell/releases"');
    expect(markup).not.toMatch(/\d+ MB/);
  });
});

describe("reading the release list", () => {
  it("returns what /app/downloads.json says, and null for no release or a failed request", async () => {
    const fetchFn = vi.fn(async () => new Response(JSON.stringify(PACKAGES), { status: 200 }));
    expect(await loadPackages(fetchFn as unknown as typeof fetch)).toEqual(PACKAGES);
    expect(fetchFn).toHaveBeenCalledWith("/app/downloads.json");

    expect(await loadPackages((async () => new Response(null, { status: 404 })) as unknown as typeof fetch)).toBeNull();
    expect(await loadPackages((async () => Promise.reject(new Error("offline"))) as unknown as typeof fetch)).toBeNull();
  });

  it("writes a size in megabytes, rounded", () => {
    expect(sizeLabel(84_300_000)).toBe("84 MB");
    expect(sizeLabel(61_900_000)).toBe("62 MB");
  });
});
