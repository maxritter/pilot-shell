import { describe, expect, it } from "vitest";
import { downloadTarget } from "./useDownload";

const release = {
  version: "12.0.0",
  packages: [
    { id: "macos-arm64", name: "QualityLayer-arm64.dmg", url: "https://example.test/arm64.dmg", size: 1 },
    { id: "macos-x64", name: "QualityLayer-x64.dmg", url: "https://example.test/x64.dmg", size: 1 },
    { id: "windows-x64", name: "QualityLayer.exe", url: "https://example.test/win.exe", size: 1 },
  ],
};

describe("the download button", () => {
  it("downloads the visitor's own package when the release has one", () => {
    expect(downloadTarget("macos-x64", release)).toEqual({ label: "Download for macOS", href: "https://example.test/x64.dmg", direct: true });
    expect(downloadTarget("windows", release).href).toBe("https://example.test/win.exe");
  });

  it("falls back to the download page for phones, unknown systems, missing packages and no release", () => {
    for (const [system, data] of [[null, release], ["linux", release], ["macos-arm64", null]] as const) {
      expect(downloadTarget(system, data)).toEqual({ label: "Download the App", href: "/download", direct: false });
    }
  });
});
