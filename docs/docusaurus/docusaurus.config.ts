import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Pilot Shell",
  tagline: "How real engineers run Claude Code and Codex — persistent knowledge, enforced quality, runtime proof",
  favicon: "img/favicon.png",

  url: "https://pilot-shell.com",
  baseUrl: "/",
  // Match Vercel's `trailingSlash: false` so canonicals point to the actually-served URL.
  // Without this, Docusaurus emits canonical=/docs/X/ but Vercel 308-redirects to /docs/X.
  // Google sees the conflict and declines to index the entry point.
  trailingSlash: false,

  organizationName: "maxritter",
  projectName: "pilot-shell",

  onBrokenLinks: "throw",

  markdown: {
    format: "md",
    hooks: {
      onBrokenMarkdownLinks: "throw",
    },
  },

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  themes: ["@easyops-cn/docusaurus-search-local"],

  scripts: [
    {
      src: "https://analytics.ahrefs.com/analytics.js",
      "data-key": "z+ZckeCmmFW1kMjAfQEXLA",
      async: true,
    },
  ],

  presets: [
    [
      "classic",
      {
        docs: {
          routeBasePath: "docs",
          sidebarPath: "./sidebars.ts",
          editUrl: "https://github.com/maxritter/pilot-shell/tree/main/docs/docusaurus/",
        },
        blog: {
          routeBasePath: "blog",
          path: "./blog",
          blogTitle: "Pilot Shell Blog",
          blogDescription:
            "Insights on Claude Code, Codex CLI, AI engineering, and the Pilot Shell platform — guides, tools, and model comparisons.",
          blogSidebarTitle: "Recent posts",
          blogSidebarCount: "ALL",
          postsPerPage: 12,
          showReadingTime: true,
          feedOptions: {
            type: ["rss", "atom"],
            title: "Pilot Shell Blog",
            description:
              "Latest posts from the Pilot Shell blog — Claude Code and Codex CLI engineering, AI tools, and model deep-dives.",
            copyright: `Copyright © ${new Date().getFullYear()} Pilot Shell.`,
          },
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
        sitemap: {
          changefreq: "weekly",
          priority: 0.7,
          ignorePatterns: ["/tags/**"],
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: "https://pilot-shell.com/logo.png",
    metadata: [
      {
        name: "keywords",
        content:
          "how real engineers run Claude Code and Codex, Claude Code, Codex CLI, OpenAI Codex, Claude Code engineering platform, Codex engineering platform, Claude Code framework, Codex framework, spec-driven development, Pilot Shell, TDD enforcement, AI coding agent, GPT-5, GPT-5.5, MCP servers, Claude Code best practices, Codex best practices",
      },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:site", content: "@maxritter" },
      { property: "og:type", content: "website" },
      { property: "og:site_name", content: "Pilot Shell" },
    ],
    colorMode: {
      defaultMode: "dark",
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "Pilot Shell",
      logo: {
        alt: "Pilot Shell Logo",
        src: "img/favicon.png",
        href: "/docs/",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "docsSidebar",
          position: "left",
          label: "Docs",
        },
        {
          to: "/blog",
          label: "Blog",
          position: "left",
        },
        {
          href: "https://pilot-shell.com",
          label: "Home",
          position: "right",
        },
        {
          href: "https://github.com/maxritter/pilot-shell",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            { label: "Getting Started", to: "/docs/getting-started/prerequisites" },
            { label: "Spec Workflow", to: "/docs/workflows/spec" },
            { label: "Hooks Pipeline", to: "/docs/features/hooks" },
            { label: "Blog", to: "/blog" },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "GitHub",
              href: "https://github.com/maxritter/pilot-shell",
            },
          ],
        },
        {
          title: "More",
          items: [{ label: "Home", href: "https://pilot-shell.com" }],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Pilot Shell. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ["bash", "json", "python", "toml"],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
