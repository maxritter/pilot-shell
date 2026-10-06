import { renderToReadableStream } from "react-dom/server.browser";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Hero from "@/components/home/Hero";
import Sections from "@/components/home/Sections";
import PricingSection from "@/components/PricingSection";
import { BANNED_WORDS } from "@/lib/banned-words";
import { FAQS, PRICING_FAQS } from "@/lib/content";
import { COMPARE, PLANS } from "@/lib/pricing";
import { DESCRIPTION } from "@/lib/product";
import { DownloadView } from "./Download";
import { readFileSync } from "node:fs";

/** The words of every page the redesign touches, read against the App's glossary. */

async function textOf(node: React.ReactNode): Promise<string> {
  const stream = await renderToReadableStream(<MemoryRouter>{node}</MemoryRouter>);
  await stream.allReady;
  const html = await new Response(stream).text();
  return html.replace(/<[^>]+>/g, " ").replaceAll("&#x27;", "'").replaceAll("&amp;", "&").replace(/\s+/g, " ");
}

describe("the site's copy", () => {
  it("uses the glossary, not the App's internal words, on the home page, download page and pricing page", async () => {
    const pages = {
      home: await textOf(<><Hero /><Sections /></>),
      download: await textOf(<DownloadView data={null} system={null} />),
      pricing: await textOf(<PricingSection />),
    };
    for (const [name, words] of Object.entries(pages)) expect(words, name).not.toMatch(BANNED_WORDS);
  });

  it("keeps the questions, the plans and the comparison table in plain words too", () => {
    const strings = [
      DESCRIPTION,
      ...[...FAQS, ...PRICING_FAQS].flatMap((f) => [f.question, f.answer]),
      ...PLANS.flatMap((p) => [p.audience, p.plus, ...p.highlights.map(([, h]) => h)]),
      ...COMPARE.flatMap((g) => g.rows.flatMap((r) => [r.feature, r.note ?? ""])),
    ];
    for (const s of strings) expect(s).not.toMatch(BANNED_WORDS);
  });

  it("calls the App the App", async () => {
    expect(await textOf(<Sections />)).not.toMatch(/cockpit/i);
  });

  it("describes the offline licence window enforced by the binary", async () => {
    // Read the real policy without importing the CLI's Bun environment into the website.
    const policy = readFileSync(new URL("../../../../qualitylayer/src/core/licence/constants.ts", import.meta.url), "utf8");
    const hours = policy.match(/export const OFFLINE_GRACE_PERIOD_HOURS = (\d+)/);
    expect(hours).not.toBeNull();
    const pricing = await textOf(<PricingSection />);
    expect(pricing).toContain(`up to ${Number(hours![1]) / 24} days after its last successful check`);
    expect(pricing).not.toContain("30 days");
  });

  it("describes the unattended upgrade that preserves Pilot's tools and memories", async () => {
    const pricing = await textOf(<PricingSection />);
    expect(pricing).toMatch(/tools.*memories stay/i);
    expect(pricing).not.toMatch(/lets you choose what happens/i);
  });

  it("tells one developer and a team the same story: the closing says both", async () => {
    const home = await textOf(<Sections />);
    expect(home).toMatch(/on your own or with your team/i);
  });
});
