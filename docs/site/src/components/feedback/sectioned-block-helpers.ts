/**
 * Pure helpers for SectionedBlockRenderer. Kept out of the .tsx so
 * react-refresh can fast-refresh the component file without warning.
 */
import type { Block } from "@/lib/annotation/types";

/**
 * Filter + sort plan-spec sections to the canonical render order.
 *
 * Preamble sections (heading === "") always come first in their original
 * order. Tasks sections (matching any heading in `tasksHeadings`) always
 * come last in their original order. Everything else is filtered to
 * `order.includes(heading)` and sorted by `order.indexOf(heading)`.
 * Unknown headings are dropped silently.
 */
export function orderSections<T extends { heading: string }>(
  sections: T[],
  order: readonly string[],
  tasksHeadings: readonly string[],
  hiddenHeadings: readonly string[] = [],
): T[] {
  const visible = sections.filter((s) => !hiddenHeadings.includes(s.heading));
  const preamble = visible.filter((s) => s.heading === "");
  const tasks = visible.filter((s) => tasksHeadings.includes(s.heading));
  // An unrecognised heading is kept, not dropped: it sorts to the end of the
  // middle group (indexOf returns -1, mapped to MAX_SAFE_INTEGER) and holds its
  // document order relative to other unrecognised ones, because
  // Array.prototype.sort is stable (ES2019+). A plan written by a skill outside
  // Pilot can therefore invent its own sections and still display them.
  const orderKey = (heading: string): number => {
    const index = order.indexOf(heading);
    return index === -1 ? Number.MAX_SAFE_INTEGER : index;
  };
  const middle = visible
    .filter((s) => s.heading !== "" && !tasksHeadings.includes(s.heading))
    .sort((a, b) => orderKey(a.heading) - orderKey(b.heading));
  return [...preamble, ...middle, ...tasks];
}

interface FieldGroup {
  label: string;
  blocks: Block[];
}

function matchLabelMarker(block: Block): string | null {
  if (block.type !== "paragraph") return null;
  const m = block.content.match(/^\*\*([A-Za-z][A-Za-z0-9 /]+):\*\*\s*(.*)$/s);
  if (!m) return null;
  return m[1].trim();
}

export function stripLabelPrefix(block: Block, label: string): Block | null {
  if (block.type !== "paragraph") return block;
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`^\\*\\*${escaped}:\\*\\*\\s*`, "s");
  const stripped = block.content.replace(re, "").trim();
  if (!stripped) return null;
  return { ...block, content: stripped };
}

function groupByLabelInternal(blocks: Block[]): FieldGroup[] {
  const groups: FieldGroup[] = [];
  let current: FieldGroup | null = null;
  for (const block of blocks) {
    const label = matchLabelMarker(block);
    if (label) {
      if (current) groups.push(current);
      const stripped = stripLabelPrefix(block, label);
      current = { label, blocks: stripped ? [stripped] : [] };
      continue;
    }
    if (current) current.blocks.push(block);
  }
  if (current) groups.push(current);
  return groups;
}

/**
 * Split a task body's blocks into the `**Objective:**` description and the
 * remaining `**Label:**` fields. The Objective renders inline below the task
 * title (matching the Console SpecTaskCard UX) so the reader sees the 2-3
 * sentence "what this task does" without a second click.
 */
export function extractObjectiveBlocks(taskBlocks: Block[]): {
  objective: Block[] | null;
  rest: Block[];
} {
  const fields = groupByLabelInternal(taskBlocks);
  const objectiveField = fields.find((f) => f.label === "Objective") ?? null;
  if (!objectiveField || objectiveField.blocks.length === 0) {
    return { objective: null, rest: taskBlocks };
  }
  const objectiveIds = new Set(objectiveField.blocks.map((b) => b.id));
  const rest = taskBlocks.filter((b) => !objectiveIds.has(b.id));
  return { objective: objectiveField.blocks, rest };
}
