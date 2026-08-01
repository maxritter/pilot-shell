import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  docsSidebar: [
    "intro",
    {
      type: "category",
      label: "Getting Started",
      collapsed: false,
      items: [
        "getting-started/prerequisites",
        "getting-started/installation",
        "getting-started/codex-cli",
      ],
    },
    {
      type: "category",
      label: "Core Workflows",
      collapsed: false,
      items: [
        "workflows/prd",
        "workflows/spec",
        "workflows/fix",
      ],
    },
    {
      type: "category",
      label: "Additional Workflows",
      collapsed: false,
      items: [
        "workflows/setup-rules",
        "workflows/create-skill",
        "workflows/benchmark",
        "workflows/ask-codex",
      ],
    },
    {
      type: "category",
      label: "Console",
      collapsed: false,
      items: [
        "features/console",
        "features/spec-collaboration",
        "features/extensions",
        "features/team-memories",
        "features/customization",
        "features/statusline",
      ],
    },
    {
      type: "category",
      label: "Quality",
      collapsed: false,
      items: [
        "features/hooks",
        "features/rules",
        "features/context-optimization",
      ],
    },
    {
      type: "category",
      label: "Automation",
      collapsed: false,
      items: [
        "features/bot",
        "features/remote-control",
      ],
    },
    {
      type: "category",
      label: "Configuration",
      collapsed: false,
      items: [
        "features/model-routing",
        "features/permission-modes",
      ],
    },
    {
      type: "category",
      label: "Tools",
      collapsed: false,
      items: [
        "features/cli",
        "features/mcp-servers",
        "features/language-servers",
        "features/open-source-tools",
      ],
    },
  ],
};

export default sidebars;
