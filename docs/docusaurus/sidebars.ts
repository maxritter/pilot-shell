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
        "getting-started/permission-modes",
      ],
    },
    {
      type: "category",
      label: "Workflows",
      collapsed: false,
      items: [
        "workflows/setup-rules",
        "workflows/create-skill",
        "workflows/prd",
        "workflows/spec",
        "workflows/fix",
        "workflows/benchmark",
        "workflows/quick-mode",
      ],
    },
    {
      type: "category",
      label: "Features",
      collapsed: false,
      items: [
        "features/console",
        "features/bot",
        "features/statusline",
        "features/model-routing",
        "features/rules",
        "features/context-optimization",
        "features/remote-control",
        "features/hooks",
        "features/extensions",
        "features/customization",
        "features/cli",
        "features/mcp-servers",
        "features/language-servers",
        "features/open-source-tools",
      ],
    },
  ],
};

export default sidebars;
