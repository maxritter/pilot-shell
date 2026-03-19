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
      ],
    },
    {
      type: "category",
      label: "Workflows",
      collapsed: false,
      items: [
        "workflows/setup-rules",
        "workflows/create-skill",
        "workflows/spec",
        "workflows/quick-mode",
      ],
    },
    {
      type: "category",
      label: "Features",
      collapsed: false,
      items: [
        "features/console",
        "features/statusline",
        "features/model-routing",
        "features/rules",
        "features/context-preservation",
        "features/remote-control",
        "features/hooks",
        "features/extensions",
        "features/cli",
        "features/mcp-servers",
        "features/language-servers",
        "features/open-source-tools",
      ],
    },
  ],
};

export default sidebars;
