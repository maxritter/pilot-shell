import { lazy, Suspense } from "react";
import NavBar from "@/components/NavBar";
import HeroSection from "@/components/HeroSection";
import InstallSection from "@/components/InstallSection";
import SEO from "@/components/SEO";

// Below-the-fold sections — split into separate chunks loaded after first paint.
const WorkflowSteps = lazy(() => import("@/components/WorkflowSteps"));
const WhatsInside = lazy(() => import("@/components/WhatsInside"));
const SpecCollabSection = lazy(() => import("@/components/SpecCollabSection"));
const ConsoleSection = lazy(() => import("@/components/ConsoleSection"));
const TestimonialsSection = lazy(() => import("@/components/TestimonialsSection"));
const FAQSection = lazy(() => import("@/components/FAQSection"));
const Footer = lazy(() => import("@/components/Footer"));

// Reserve space while a chunk is in flight. The exact height isn't critical
// since CLS is already 0 — but a placeholder avoids a brief jump.
const SectionFallback = () => <div aria-hidden="true" style={{ minHeight: "40vh" }} />;

const Index = () => {
  const websiteStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Pilot Shell",
    url: "https://pilot-shell.com/",
    description:
      "Spec-driven planning, enforced TDD, persistent memory, and quality automation for Claude Code, with Codex compatibility for supported integrations.",
    inLanguage: "en-US",
    publisher: {
      "@type": "Organization",
      name: "Pilot Shell",
      url: "https://pilot-shell.com/",
      logo: {
        "@type": "ImageObject",
        url: "https://pilot-shell.com/logo.png",
      },
      sameAs: [
        "https://github.com/maxritter/pilot-shell",
        "https://www.linkedin.com/in/rittermax/",
      ],
    },
  };

  const breadcrumbStructuredData = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: "https://pilot-shell.com/",
      },
    ],
  };

  const softwareStructuredData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "Pilot Shell",
    description:
      "Spec-driven planning, enforced TDD, persistent memory, and quality automation for Claude Code, with Codex compatibility for supported integrations.",
    applicationCategory: "DeveloperApplication",
    applicationSubCategory: "AI Development Tools",
    operatingSystem: "Linux, macOS, Windows",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
    },
    author: {
      "@type": "Person",
      name: "Max Ritter",
      url: "https://maxritter.net/",
    },
    license: "https://github.com/maxritter/pilot-shell/blob/main/LICENSE",
    url: "https://github.com/maxritter/pilot-shell",
    downloadUrl: "https://github.com/maxritter/pilot-shell",
  };

  return (
    <>
      <SEO
        title="Spec-driven development for Claude Code & Codex CLI"
        description="Spec-driven planning, enforced TDD, persistent memory, and quality automation for Claude Code, with Codex compatibility for supported integrations across Python, TypeScript, Go, and C#."
        structuredData={[
          websiteStructuredData,
          breadcrumbStructuredData,
          softwareStructuredData,
        ]}
      />
      <NavBar />
      <main className="min-h-screen bg-background">
        <HeroSection />
        <InstallSection />
        <Suspense fallback={<SectionFallback />}>
          <WhatsInside />
          <WorkflowSteps />
          <SpecCollabSection />
          <ConsoleSection />
          <TestimonialsSection />
          <FAQSection />
        </Suspense>
      </main>
      <Suspense fallback={null}>
        <Footer />
      </Suspense>
    </>
  );
};

export default Index;
