import { useEffect, useState, type CSSProperties } from "react";
import { Button } from "@/components/ui/button";
import { PolarEmbedCheckout } from "@polar-sh/checkout/embed";
import Questions from "@/components/Questions";
import { PRICING_FAQS } from "@/lib/content";
import { PORTAL_URL } from "@/lib/links";
import { OFFLINE_DAYS } from "@/lib/product";
import { COMPARE, PLANS, USE_EMBED_CHECKOUT, type Cell, type Hue, type Plan } from "@/lib/pricing";

const HUE: Record<Hue, string> = { plan: "var(--hl-violet)", build: "var(--ql-accent)", verify: "var(--hl-teal)", review: "var(--ql-amber-ink)" };
const hue = (h: Hue) => ({ "--g": HUE[h] }) as CSSProperties;

type Billing = "monthly" | "yearly";

/** Live checkouts open Polar's overlay in production; Enterprise is a mail link. */
const checkoutProps = (plan: Plan) =>
  plan.id === "enterprise" ? {}
    : USE_EMBED_CHECKOUT ? { "data-polar-checkout": true, "data-polar-checkout-theme": "dark" }
      : { target: "_blank", rel: "noopener" };

function CellMark({ value }: { value: Cell }) {
  if (value === "request") return <span className="pr-req">On request</span>;
  if (value) return <span role="img" aria-label="Included" className="pr-ck" style={hue("build")} />;
  return <span role="img" aria-label="Not included" className="pr-dash" />;
}

/** The price as the switch shows it: per month, and for yearly the full year struck through beside what it costs. */
function Price({ plan, billing }: { plan: Plan; billing: Billing }) {
  if (plan.price === "Custom") {
    return (
      <>
        <div className="pr-price"><b className="pr-amt">Custom</b><span className="pr-per">{plan.per}</span></div>
        <p className="pr-bill">Seats, hosting and terms set together</p>
      </>
    );
  }
  const { monthly, yearly } = plan.price;
  const seat = plan.id === "team" ? " per seat" : "";
  return (
    <>
      <div className="pr-price"><b className="pr-amt">${billing === "yearly" ? yearly : monthly}</b><span className="pr-per">{plan.per}</span></div>
      {billing === "yearly" ? (
        <p className="pr-bill"><s aria-label={`instead of $${monthly * 12}`}>${monthly * 12}</s> ${yearly * 12}{seat} billed yearly</p>
      ) : (
        <p className="pr-bill">Billed monthly · cancel any time</p>
      )}
    </>
  );
}

const PricingSection = () => {
  const [billing, setBilling] = useState<Billing>("yearly");
  useEffect(() => {
    if (USE_EMBED_CHECKOUT) PolarEmbedCheckout.init();
  }, []);

  return (
    <div className="pr-root">
      <section id="plans" className="pr-top-sec" aria-labelledby="pr-h">
        <div className="pr-wrap">
          <h1 id="pr-h" className="pr-h1">Pricing</h1>
          <p className="pr-lead">Every plan starts with a 7-day trial the first time you run QualityLayer. One price per developer, with no limits on tasks, repositories or agents. Your Claude Code or Codex subscription stays as it is.</p>
          <div className="pr-seg" role="group" aria-label="Billing">
            <Button type="button" variant={billing === "monthly" ? "default" : "ghost"} aria-pressed={billing === "monthly"} onClick={() => setBilling("monthly")}>Monthly</Button>
            <Button type="button" variant={billing === "yearly" ? "default" : "ghost"} aria-pressed={billing === "yearly"} onClick={() => setBilling("yearly")}>Yearly <span className="pr-save">Save 20%</span></Button>
          </div>
          <div className="pr-plans">
            {PLANS.map((plan) => (
              <article key={plan.id} className="pr-plan" aria-labelledby={`${plan.id}-h`}>
                <div className="pr-top">
                  <div><h2 id={`${plan.id}-h`} className="pr-name">{plan.name}</h2><p className="pr-aud">{plan.audience}</p></div>
                  {plan.badge ? <span className="pr-badge req">{plan.badge}</span> : null}
                </div>
                <Price plan={plan} billing={billing} />
                <Button asChild size="xl" variant={plan.id === "enterprise" ? "outline" : "default"} className="pr-btn"><a href={typeof plan.href === "string" ? plan.href : plan.href[billing]} {...checkoutProps(plan)}>{plan.cta}</a></Button>
                <p className="pr-plus">{plan.plus}</p>
                <ul className="pr-hl">
                  {plan.highlights.map(([h, text]) => (
                    <li key={text} className="pr-hli" style={hue(h)}><span aria-hidden="true" className="pr-ck" /><span className="pr-hlt">{text}</span></li>
                  ))}
                </ul>
                <a className="pr-more" href="#compare">Compare the plans</a>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="compare" className="pr-sec sunk" aria-labelledby="compare-h">
        <div className="pr-wrap">
          <h2 id="compare-h" className="pr-h2">Compare the plans</h2>
          <div className="pr-table" role="table" aria-label="Compare Solo, Team and Enterprise">
            <div className="pr-tr pr-th" role="row">
              <span role="columnheader">Feature</span>
              <span className="pr-c" role="columnheader">Solo</span>
              <span className="pr-c" role="columnheader">Team</span>
              <span className="pr-c" role="columnheader">Enterprise</span>
            </div>
            {COMPARE.map((group) => (
              <div key={group.name} role="rowgroup" style={{ display: "contents" }}>
                <div className="pr-tr pr-tg" role="row" style={hue(group.hue)}><span role="rowheader">{group.name}</span></div>
                {group.rows.map((r) => (
                  <div key={r.feature} className="pr-tr" role="row">
                    <span role="rowheader">{r.feature}{r.note ? <span className="pr-note">{r.note}</span> : null}</span>
                    <span className="pr-c" role="cell"><CellMark value={r.solo} /></span>
                    <span className="pr-c" role="cell"><CellMark value={r.team} /></span>
                    <span className="pr-c" role="cell"><CellMark value={r.enterprise} /></span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="pr-sec" aria-labelledby="licence-h">
        <div className="pr-wrap">
          <h2 id="licence-h" className="pr-h2">How the licence works</h2>
          <div className="pr-how">
            <div className="pr-hi" style={hue("build")}><b>Activate once</b><span>Paste your key in the App on first start, or run <span className="pr-code">qualitylayer licence activate &lt;key&gt;</span>. Manage invoices, seats and payment in <a href={PORTAL_URL} target="_blank" rel="noopener noreferrer">the customer portal</a>.</span></div>
            <div className="pr-hi" style={hue("verify")}><b>Works offline</b><span>The licence is checked once a day. Without a connection, a paid licence works for up to {OFFLINE_DAYS} days after its last successful check.</span></div>
            <div className="pr-hi" style={hue("plan")}><b>Coming from Pilot Shell</b><span>Your subscription and your plans carry over, at the price you pay today. The App or Pilot Shell’s updater moves you over automatically. Pilot’s tools and memories stay; ask your agent to remove what you no longer use.</span></div>
          </div>
        </div>
      </section>

      <Questions faqs={PRICING_FAQS} id="pricing-faq" sunk />
    </div>
  );
};

export default PricingSection;
