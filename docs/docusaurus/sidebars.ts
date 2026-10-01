import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

/** A group of workflow steps: its short landing page, then one page per step. */
const group = (label: string, id: string, steps: string[]) => ({
  type: "category" as const,
  label,
  collapsed: true,
  link: { type: "doc" as const, id },
  items: steps.map((step) => `${id}/${step}`),
});

const sidebars: SidebarsConfig = {
  docsSidebar: [
    "intro",
    "reference/changelog",
    { type: "category", label: "Get started", collapsed: false, items: ["install", "first-task"] },
    { type: "category", label: "How a task works", collapsed: false, items: [
      "workflow/overview",
      group("Plan", "workflow/plan", ["frame", "research", "diagnose", "design", "outline"]),
      group("Build", "workflow/build", ["handoff", "slices", "checks", "simplify"]),
      group("Check and ship", "workflow/check", ["verify", "review", "shipped", "stops"]),
    ] },
    { type: "category", label: "Cockpit and team", collapsed: false, items: ["cockpit", "team/plans", "team/changes"] },
    { type: "category", label: "Reference", collapsed: false, items: [
      "reference/commands", "reference/settings", "reference/files",
    ] },
  ],
};

export default sidebars;
