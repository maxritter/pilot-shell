import { lazy, Suspense } from "react";
import NavBar from "@/components/NavBar";
import SEO from "@/components/SEO";

const PricingSection = lazy(() => import("@/components/PricingSection"));
const Footer = lazy(() => import("@/components/Footer"));

const Pricing = () => (
  <>
    <SEO
      title="Pricing — Pilot Shell for Claude Code & Codex CLI"
      description="Pilot Shell pricing for solo developers and teams, with persistent context, enforced quality, runtime proof, and supported integrations for Claude Code and Codex CLI."
      canonicalUrl="https://pilot-shell.com/pricing"
    />
    <NavBar />
    <main className="min-h-screen bg-background">
      <Suspense fallback={<div aria-hidden="true" style={{ minHeight: "60vh" }} />}>
        <PricingSection />
        <Footer />
      </Suspense>
    </main>
  </>
);

export default Pricing;
