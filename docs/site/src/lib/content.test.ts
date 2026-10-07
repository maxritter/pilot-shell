import { describe, expect, it } from "vitest";
import { FAQS, PRICING_FAQS } from "./content";
import { CONTACT_EMAIL, INSTALL_COMMAND, SITE_URL } from "./product";
import { COMPARE, PLANS } from "./pricing";

describe("FAQ", () => {
  it("answers in plain text, so structured data can reuse it", () => {
    for (const faq of [...FAQS, ...PRICING_FAQS]) {
      expect(faq.question.endsWith("?")).toBe(true);
      expect(faq.answer).not.toMatch(/<[^>]+>/);
    }
  });

  it("asks each question once", () => {
    const home = FAQS.map((faq) => faq.question);
    expect(new Set(home).size).toBe(home.length);
  });

  it("answers for one developer and for a team", () => {
    const answers = FAQS.map((faq) => `${faq.question} ${faq.answer}`).join(" ");
    expect(answers).toMatch(/on your own|alone/i);
    expect(answers).toMatch(/team/i);
  });

  it("says what a feedback report sends, as the plan lists it, and what it never sends", () => {
    const answer = FAQS.find((faq) => /feedback/i.test(faq.question))?.answer ?? "";
    expect(answer).toMatch(/private issue/i);
    for (const sent of [/versions of the App, the command line, Claude Code and Codex/, /your system and its architecture/, /the kind of page you were on/, /your licence/, /errors of the last hour by kind/]) expect(answer).toMatch(sent);
    expect(answer).toMatch(/never include your code, the text of a plan or document, task titles, repository or branch names, or file paths\./);
    expect(answer).toMatch(/Screenshots can show code or plans\./);
  });

  it("distinguishes the coding agent's provider from QualityLayer sharing and feedback", () => {
    for (const faq of [...FAQS, ...PRICING_FAQS].filter((f) => f.question === "Does my code leave my computer?")) {
      expect(faq.answer).toMatch(/your (AI |coding )?agent.*provider/i);
      expect(faq.answer).toMatch(/screenshot you attach to a feedback report/i);
      expect(faq.answer).not.toMatch(/^No\.|the one way it can leave/i);
    }
  });

  it("calls the second opinion one thing", () => {
    for (const faq of [...FAQS, ...PRICING_FAQS]) expect(faq.answer).not.toMatch(/vendor/i);
  });

  it("names only the agents the App sets up", () => {
    for (const faq of [...FAQS, ...PRICING_FAQS]) expect(faq.answer).not.toMatch(/grok/i);
  });
});

describe("product facts", () => {
  it("serves the installer from the product's own domain", () => {
    expect(INSTALL_COMMAND).toBe(`curl -fsSL ${SITE_URL}/install.sh | bash`);
    expect(SITE_URL).toBe("https://qualitylayer.dev");
  });

  it("sells Solo and Team through live checkouts, and Enterprise by mail", () => {
    expect(PLANS.map((plan) => plan.id)).toEqual(["solo", "team", "enterprise"]);
    for (const plan of PLANS.filter((p) => p.id !== "enterprise")) {
      const { price, href } = plan;
      if (price === "Custom" || typeof href === "string") throw new Error(`${plan.id} must sell monthly and yearly`);
      // Yearly is 20% off the monthly price, in whole dollars.
      expect(price.yearly).toBe(price.monthly * 0.8);
      for (const link of [href.monthly, href.yearly]) expect(link).toMatch(/^https:\/\/(sandbox-api\.polar\.sh|buy\.polar\.sh)\//);
    }
    expect(String(PLANS.find((p) => p.id === "enterprise")?.href)).toMatch(new RegExp(`^mailto:${CONTACT_EMAIL}\\?`));
  });

  it("gives every plan four highlights, as the cards are drawn", () => {
    for (const plan of PLANS) expect(plan.highlights).toHaveLength(4);
  });

  it("offers the Enterprise-only rows on request, and nothing else", () => {
    const enterprise = COMPARE.find((g) => g.name === "Enterprise");
    expect(enterprise?.rows.every((r) => r.enterprise === "request" && !r.solo && !r.team)).toBe(true);
    const others = COMPARE.filter((g) => g.name !== "Enterprise").flatMap((g) => g.rows);
    expect(others.every((r) => r.enterprise !== "request")).toBe(true);
  });
});
