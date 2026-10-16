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

const PRIVATE_PAGES = {
  "/billing": {
    title: "Subscription & billing | QualityLayer",
    description: "Manage invoices, seats and payment in your billing account.",
    robots: "noindex,nofollow",
  },
  "/checkout/success": {
    title: "Purchase confirmation | QualityLayer",
    description: "Check your subscription and activate QualityLayer with your licence key.",
    robots: "noindex,nofollow",
  },
  "/open": {
    title: "Open in the QualityLayer App",
    description: "Open the question or the task from the message in the QualityLayer App.",
    robots: "noindex",
  },
} as const;

export function pageMetadata(pathname: string) {
  const page = PUBLIC_PAGES[pathname as keyof typeof PUBLIC_PAGES];
  const privatePath = pathname.startsWith("/open/") ? "/open" : pathname;
  const privatePage = PRIVATE_PAGES[privatePath as keyof typeof PRIVATE_PAGES];
  return {
    title: page?.title ?? privatePage?.title ?? "QualityLayer",
    description: page?.description ?? privatePage?.description ?? "Open your QualityLayer task in the App.",
    canonicalUrl: `${SITE_URL}${pathname}`,
    robots: page ? INDEXABLE_ROBOTS : privatePage?.robots ?? "noindex, follow",
  };
}

/** Keep JSON text inside its inert script element, even if content contains HTML. */
export function serializeStructuredData(data: object | object[]) {
  return JSON.stringify(data).replaceAll("<", "\\u003c");
}
