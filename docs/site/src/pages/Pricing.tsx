import { lazy, Suspense } from "react";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { PRICING_FAQS } from "@/lib/content";
import { faqStructuredData, PRICING_APPLICATION } from "@/lib/structured-data";

const structuredData = [PRICING_APPLICATION, faqStructuredData(PRICING_FAQS)];

const PricingSection = lazy(() => import("@/components/PricingSection"));

const Pricing = () => (
  <>
    <SEO structuredData={structuredData} />
    <Page className="page-pricing">
      <Suspense fallback={<div aria-hidden="true" style={{ minHeight: "60vh" }} />}>
        <PricingSection />
      </Suspense>
    </Page>
  </>
);

export default Pricing;
