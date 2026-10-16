import { SHARE_DESCRIPTION, SITE_URL, SLOGAN } from "./product.ts";

export const PUBLIC_PAGES = {
  "/": { title: `QualityLayer: ${SLOGAN}`, description: SHARE_DESCRIPTION },
  "/pricing": {
    title: "Pricing — QualityLayer",
    description: "QualityLayer pricing for developers, teams and companies. Every plan starts with a 7-day trial.",
  },
  "/download": {
    title: "Download the QualityLayer App — QualityLayer",
    description: "Download QualityLayer for macOS, Windows and Linux. Plan and review changes with Claude Code, Codex and your team.",
  },
} as const;

export const INDEXABLE_ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1";

export function pageMetadata(pathname: string) {
  const page = PUBLIC_PAGES[pathname as keyof typeof PUBLIC_PAGES];
  return {
    title: page?.title ?? "QualityLayer",
    description: page?.description ?? "Open your QualityLayer task in the App.",
    canonicalUrl: `${SITE_URL}${pathname}`,
    robots: page ? INDEXABLE_ROBOTS : "noindex, follow",
  };
}
