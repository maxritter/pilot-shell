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
  title = "Pilot Shell — How real engineers run Claude Code and Codex",
  description = "How real engineers run Claude Code and Codex: spec-driven planning, enforced TDD, persistent memory, and quality hooks for Python, TypeScript, Go, and C#. Make your agents production-ready.",
  keywords = "how real engineers run Claude Code and Codex, Claude Code, Codex CLI, OpenAI Codex, Claude Code engineering platform, Codex engineering platform, Claude Code framework, Codex framework, spec-driven development, Pilot Shell, Anthropic Claude, OpenAI GPT-5, AI pair programming, TDD enforcement, AI coding agent, Claude Opus 5, Claude Sonnet 5, GPT-5, GPT-5.5, MCP servers, Claude Code productivity, Codex productivity, AI development environment, Claude Code best practices, Codex best practices",
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
