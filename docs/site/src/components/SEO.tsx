import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router-dom";
import { SITE_URL } from "@/lib/product";
import { pageMetadata, serializeStructuredData } from "@/lib/seo";

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonicalUrl?: string;
  ogImage?: string;
  type?: string;
  structuredData?: object | object[];
  robots?: string;
}

/** Used by both the browser and the build-time renderer. */
const SEO = ({
  title,
  description,
  keywords = "software factory, human in the loop, visual planning, claude code, codex cli, ai coding agent, spec driven development, plan review, QualityLayer",
  canonicalUrl,
  ogImage = `${SITE_URL}/og.png`,
  type = "website",
  structuredData,
  robots,
}: SEOProps) => {
  const defaults = pageMetadata(useLocation().pathname);
  title ??= defaults.title;
  description ??= defaults.description;
  canonicalUrl ??= defaults.canonicalUrl;
  robots ??= defaults.robots;
  return (
    <Helmet>
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="robots" content={robots} />

      <link rel="canonical" href={canonicalUrl} />

      <meta property="og:type" content={type} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="QualityLayer" />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={canonicalUrl} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />

      {structuredData && <script type="application/ld+json">{serializeStructuredData(structuredData)}</script>}
    </Helmet>
  );
};

export default SEO;
