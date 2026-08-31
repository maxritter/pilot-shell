import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonicalUrl?: string;
  ogImage?: string;
  type?: string;
  structuredData?: object | object[];
}

const SEO = ({
  /*
   * KEYWORDS retain measured US search terms (DataForSEO, 2026-08). The TITLE
   * and DESCRIPTION carry the product's harness-first positioning instead of
   * making one optional Pilot workflow look like the whole product:
   *
   *   codex cli                  27100/mo   competition 30
   *   claude code skills         12100/mo   competition  9
   *   spec driven development     6600/mo   competition 42
   *   claude code agents          5400/mo   competition 21
   *   claude code plugins         5400/mo   competition  3
   *   claude code hooks           3600/mo   competition  2
   *   claude code subagents       2900/mo   competition  5
   *   claude code mcp             2900/mo   competition  9
   *   claude code framework         40/mo   <- what the old keywords led with
   *
   * "claude code" itself is 550000/mo but navigational to Anthropic, so it is
   * carried for relevance and never chased as a target.
   *
   * Do not "optimize" the description into a keyword list. It is product positioning, not an SEO
   * slot, and it is the sentence Slack, LinkedIn and X show when the site is
   * shared. An earlier pass rewrote it into a feature list (skills, hooks,
   * subagents, MCP) and that was rejected: it understates what Pilot Shell
   * does. Keep it, and the og:/twitter: variants, in the product's own words.
   *
   * The title stays around 60 characters so search results remain readable.
   */
  title = "Pilot Shell — Engineering harness for Claude Code & Codex",
  description = "Professional context, enforced quality, persistent knowledge, code intelligence, and runtime proof for Claude Code and Codex — with Pilot workflows when you want their contract.",
  keywords = "claude code skills, codex cli, spec driven development, claude code agents, claude code plugins, claude code hooks, claude code subagents, claude code mcp, claude code setup, claude code best practices, Pilot Shell",
  canonicalUrl = "https://pilot-shell.com/",
  ogImage = "https://pilot-shell.com/logo.png",
  type = "website",
  structuredData
}: SEOProps) => {
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

      {/* Canonical URL */}
      <link rel="canonical" href={canonicalUrl} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="Pilot Shell" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={canonicalUrl} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />

      {/* Structured Data */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
};

export default SEO;
