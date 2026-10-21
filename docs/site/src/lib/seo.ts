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
  "/compare": {
    title: "Compare QualityLayer with spec-driven development tools",
    description: "Compare QualityLayer with HumanLayer, GitHub Spec Kit, OpenSpec and Kiro. See their strengths, agent support and approaches to verification and review.",
  },
  "/compare/humanlayer": {
    title: "QualityLayer vs HumanLayer: planning, verification and review",
    description: "Considering a HumanLayer alternative? Compare agent support, collaborative planning, recorded verification and human review in QualityLayer and HumanLayer.",
  },
  "/compare/spec-kit": {
    title: "QualityLayer vs GitHub Spec Kit: specs, proof and review",
    description: "Looking for a Spec Kit alternative? Compare GitHub Spec Kit's customizable spec workflows with QualityLayer's visual planning, verification and human approval.",
  },
  "/compare/openspec": {
    title: "QualityLayer vs OpenSpec: change proposals and verification",
    description: "Compare OpenSpec's flexible change proposals, spec updates and verification with QualityLayer's visual planning, recorded evidence and human review process.",
  },
  "/compare/kiro": {
    title: "QualityLayer vs Kiro: spec workflows and code verification",
    description: "Compare Kiro's integrated specs and property-based testing with QualityLayer's Claude Code and Codex workflow, recorded verification and human review.",
  },
  "/best-spec-driven-development-tools": {
    title: "Best spec-driven development tools for your workflow | QualityLayer",
    description: "A practical comparison of spec-driven development tools: QualityLayer, HumanLayer, GitHub Spec Kit, OpenSpec and Kiro. Choose by workflow, review and verification.",
  },
  "/imprint": {
    title: "Imprint — QualityLayer",
    description: "Who sells QualityLayer and how to reach us: address, e-mail and VAT ID.",
  },
  "/privacy": {
    title: "Privacy policy — QualityLayer",
    description: "What QualityLayer sends, to whom, why and for how long, and your rights under the GDPR.",
  },
  "/terms": {
    title: "Terms of service — QualityLayer",
    description: "The terms for qualitylayer.dev, the QualityLayer App and the team service.",
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
