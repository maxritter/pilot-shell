import { useEffect, useState } from "react";
import { type Card, loadPackages, type Packages, systemOf } from "@/lib/downloads";

const NAMES: Record<Card, string> = { "macos-arm64": "macOS", "macos-x64": "macOS", windows: "Windows", linux: "Linux" };
const PACKAGE: Record<Card, string> = { "macos-arm64": "macos-arm64", "macos-x64": "macos-x64", windows: "windows-x64", linux: "linux-x64" };

/**
 * The download button's label and target: the visitor's own package when the newest release
 * and their system are known, otherwise the download page with every system on it.
 */
export function useDownload(): { label: string; href: string; direct: boolean } {
  const [data, setData] = useState<Packages | null>(null);
  const [system, setSystem] = useState<Card | null>(() => (typeof navigator === "undefined" ? null : systemOf(navigator.userAgent)));

  useEffect(() => {
    let live = true;
    void loadPackages().then((loaded) => live && setData(loaded));
    // As on the download page: only Chromium says which chip a Mac has; the others get Apple silicon.
    const hints = (navigator as Navigator & { userAgentData?: { getHighEntropyValues(keys: string[]): Promise<{ architecture?: string }> } }).userAgentData;
    void hints?.getHighEntropyValues(["architecture"]).then((values) => live && setSystem(systemOf(navigator.userAgent, values.architecture)), () => undefined);
    return () => {
      live = false;
    };
  }, []);

  return downloadTarget(system, data);
}

export function downloadTarget(system: Card | null, data: Packages | null): { label: string; href: string; direct: boolean } {
  const url = system ? data?.packages.find((p) => p.id === PACKAGE[system])?.url : undefined;
  if (system && url) return { label: `Download for ${NAMES[system]}`, href: url, direct: true };
  return { label: "Download the App", href: "/download", direct: false };
}
