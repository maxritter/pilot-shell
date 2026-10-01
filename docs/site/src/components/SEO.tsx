import { Helmet } from "react-helmet-async";
import { DESCRIPTION, SITE_URL } from "@/lib/product";

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonicalUrl?: string;
  ogImage?: string;
  type?: string;
  structuredData?: object | object[];
}

/*
 * The defaults here must match the head of index.html by hand: this is a client-rendered
 * SPA, so index.html is what Slack, LinkedIn and X unfurls and non-JavaScript crawlers see,
 * and react-helmet-async only rewrites the head after hydration.
 *
 * The description is product positioning, not a keyword slot: it is the sentence shown when
 * the site is shared. Keep it in the product's own words.
 */
const SEO = ({
  title = "QualityLayer — The software factory for your coding agents",
  description = DESCRIPTION,
  keywords = "claude code, codex cli, ai coding agent, spec driven development, agent planning, code verification, QualityLayer",
  canonicalUrl = `${SITE_URL}/`,
  ogImage = `${SITE_URL}/og.png`,
  type = "website",
  structuredData,
}: SEOProps) => {
  return (
    <Helmet>
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

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

      {structuredData && <script type="application/ld+json">{JSON.stringify(structuredData)}</script>}
    </Helmet>
  );
};

export default SEO;
