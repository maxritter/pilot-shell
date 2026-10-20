import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PLANS } from "@/lib/pricing";
import CheckoutLink from "./CheckoutLink";

describe("subscription checkout links", () => {
  for (const plan of PLANS.filter((plan) => plan.id !== "enterprise")) {
    for (const billing of ["monthly", "yearly"] as const) {
      it(`opens hosted ${plan.id} ${billing} checkout without an embed or API dependency`, () => {
        const href = typeof plan.href === "string" ? plan.href : plan.href[billing];
        const html = renderToStaticMarkup(<CheckoutLink plan={plan.id as "solo" | "team"} billing={billing} href={href} className="purchase">{plan.cta}</CheckoutLink>);
        expect(new URL(href).origin).toBe("https://buy.polar.sh");
        expect(html).toContain(`href="${href}"`);
        expect(html).toContain(`data-checkout-plan="${plan.id}"`);
        expect(html).toContain(`data-checkout-billing="${billing}"`);
        expect(html).toContain('class="purchase"');
        expect(html).not.toMatch(/iframe|dialog|aria-disabled|aria-busy|embed_origin/);
      });
    }
  }
});
