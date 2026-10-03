import { lazy, Suspense } from "react";
import Hero from "@/components/home/Hero";
import Page from "@/components/Page";
import SEO from "@/components/SEO";
import { FAQS } from "@/lib/content";
import { AUTHOR_NAME, AUTHOR_URL, DESCRIPTION, GITHUB_URL, SITE_URL } from "@/lib/product";
import { DemoTourProvider } from "@/components/home/demoTour";

// Below the fold: one chunk, loaded after first paint.
const Sections = lazy(() => import("@/components/home/Sections"));

const structuredData = [
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "QualityLayer",
    url: `${SITE_URL}/`,
    description: DESCRIPTION,
    inLanguage: "en-US",
    publisher: {
      "@type": "Organization",
      name: "QualityLayer",
      url: `${SITE_URL}/`,
      logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` },
      sameAs: [GITHUB_URL, "https://www.linkedin.com/in/rittermax/"],
    },
  },
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "QualityLayer",
    description: DESCRIPTION,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "macOS, Linux, Windows",
    author: { "@type": "Person", name: AUTHOR_NAME, url: AUTHOR_URL },
    url: `${SITE_URL}/`,
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQS.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: { "@type": "Answer", text: faq.answer },
    })),
  },
];

const Index = () => (
  <>
    <SEO structuredData={structuredData} />
    <Page>
      <DemoTourProvider>
      <Hero />
      <Suspense fallback={<div aria-hidden="true" style={{ minHeight: "40vh" }} />}>
        <Sections />
      </Suspense>
      </DemoTourProvider>
    </Page>
  </>
);

export default Index;
