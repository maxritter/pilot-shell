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
});

describe("product facts", () => {
  it("serves the installer from the product's own domain", () => {
    expect(INSTALL_COMMAND).toBe(`curl -fsSL ${SITE_URL}/install.sh | bash`);
    expect(SITE_URL).toBe("https://qualitylayer.dev");
  });

  it("sells Solo and Team through live checkouts, and Enterprise by mail", () => {
    expect(PLANS.map((plan) => plan.id)).toEqual(["solo", "team", "enterprise"]);
    for (const plan of PLANS.filter((p) => p.id !== "enterprise")) {
      expect(plan.price).toBeGreaterThan(0);
      expect(plan.href).toMatch(/^https:\/\/buy\.polar\.sh\//);
    }
    expect(PLANS.find((p) => p.id === "enterprise")?.href).toMatch(new RegExp(`^mailto:${CONTACT_EMAIL}\\?`));
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
