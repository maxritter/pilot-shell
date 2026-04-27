import NavBar from "@/components/NavBar";
import HeroSection from "@/components/HeroSection";
import InstallSection from "@/components/InstallSection";
import WorkflowSteps from "@/components/WorkflowSteps";
import WhatsInside from "@/components/WhatsInside";
import ConsoleSection from "@/components/ConsoleSection";
import DemoSection from "@/components/DemoSection";
import PricingSection from "@/components/PricingSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import FAQSection from "@/components/FAQSection";
import Footer from "@/components/Footer";
import SEO from "@/components/SEO";

const Index = () => {
  const websiteStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Pilot Shell",
    url: "https://pilot-shell.com/",
    description:
      "The Claude Code engineering platform: spec-driven planning, enforced TDD, persistent memory, and quality hooks. Make Claude Code production-ready.",
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
      "The Claude Code engineering platform: spec-driven planning, enforced TDD, persistent memory, and quality hooks. Make Claude Code production-ready.",
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
        title="Pilot Shell — The Claude Code Engineering Platform"
        description="The Claude Code engineering platform: spec-driven planning, enforced TDD, persistent memory, and quality hooks for Python, TypeScript, and Go. Make Claude Code production-ready."
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
        <WhatsInside />
        <WorkflowSteps />
        <ConsoleSection />
        <PricingSection />
        <TestimonialsSection />
        <DemoSection />
        <FAQSection />
        <Footer />
      </main>
    </>
  );
};

export default Index;
