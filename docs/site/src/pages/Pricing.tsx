import { lazy, Suspense } from "react";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { SITE_URL } from "@/lib/product";

const PricingSection = lazy(() => import("@/components/PricingSection"));

const Pricing = () => (
  <>
    <SEO
      title="Pricing — QualityLayer"
      description="QualityLayer pricing for one developer, for teams, and for companies. Every plan starts with a 7-day trial."
      canonicalUrl={`${SITE_URL}/pricing`}
    />
    <Page className="page-pricing">
      <Suspense fallback={<div aria-hidden="true" style={{ minHeight: "60vh" }} />}>
        <PricingSection />
      </Suspense>
    </Page>
  </>
);

export default Pricing;
