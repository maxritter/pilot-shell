import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Pilot Shell",
  tagline: "The Claude Code engineering platform — spec-driven plans, enforced tests, persistent knowledge",
  favicon: "img/favicon.png",

  url: "https://pilot-shell.com",
  baseUrl: "/",
  // Match Vercel's `trailingSlash: false` so canonicals point to the actually-served URL.
  // Without this, Docusaurus emits canonical=/docs/X/ but Vercel 308-redirects to /docs/X.
  // Google sees the conflict and declines to index the entry point.
  trailingSlash: false,

  organizationName: "maxritter",
  projectName: "pilot-shell",

  onBrokenLinks: "warn",

  markdown: {
    format: "md",
    hooks: {
      onBrokenMarkdownLinks: "warn",
    },
  },

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  themes: ["@easyops-cn/docusaurus-search-local"],

  presets: [
    [
      "classic",
      {
        docs: {
          routeBasePath: "docs",
          sidebarPath: "./sidebars.ts",
          editUrl:
            "https://github.com/maxritter/pilot-shell/tree/main/docs/docusaurus/",
        },
        blog: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: "https://pilot-shell.com/logo.png",
    metadata: [
      { name: "keywords", content: "Claude Code engineering platform, Claude Code, Claude Code platform, Claude Code framework, spec-driven development, Pilot Shell, TDD enforcement, AI coding agent, MCP servers, Claude Code best practices" },
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
          items: [
            { label: "Home", href: "https://pilot-shell.com" },
          ],
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
