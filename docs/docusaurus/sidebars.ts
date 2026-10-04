import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  docsSidebar: [
    "intro",
    "reference/changelog",
    { type: "category", label: "Get started", collapsed: false, items: [
      "install", "agents/other", "first-task", "updating", "moving-from-pilot-shell",
    ] },
    { type: "category", label: "The five steps", collapsed: false, items: [
      "steps/discuss", "steps/plan", "steps/implement", "steps/verify", "steps/review",
    ] },
    { type: "category", label: "App and team", collapsed: false, items: [
      "app", "team/plans", "team/agents", "team/changes",
    ] },
    { type: "category", label: "Reference", collapsed: false, items: [
      "reference/commands", "reference/settings", "reference/files",
    ] },
  ],
};

export default sidebars;
