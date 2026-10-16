import { lazy, Suspense } from "react";
import Page from "@/components/Page";
import SEO from "@/components/SEO";

const PricingSection = lazy(() => import("@/components/PricingSection"));

const Pricing = () => (
  <>
    <SEO />
    <Page className="page-pricing">
      <Suspense fallback={<div aria-hidden="true" style={{ minHeight: "60vh" }} />}>
        <PricingSection />
      </Suspense>
    </Page>
  </>
);

export default Pricing;
