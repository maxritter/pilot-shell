import { useState, useEffect, useMemo } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlockRenderer } from "./BlockRenderer";
import type { Annotation, Block } from "@/lib/annotation/types";

/**
 * Section-aware wrapper around BlockRenderer for pilot-shell.com / shared
 * spec viewing.
 *
 * Ported from console/src/ui/viewer/views/Spec/annotation/SectionedBlockRenderer.tsx
 * — kept in sync. Same grouping logic; classnames adapted to shadcn tokens
 * (border-border / bg-card / text-muted-foreground) used by the marketing
 * site.
 *
 * Grouping levels:
 *  - H2 (`##`) → top-level collapsible section.
 *  - Inside `## Implementation Tasks` / `## Tasks`, `### Task N:` H3 → per-task collapsible.
 *  - Inside each task, paragraphs whose content is `**Label:**` → per-field collapsible.
 *
 * Annotation anchoring is preserved: the inner BlockRenderer still renders
 * each Block by its stable id, so the existing annotation overlay works
 * unchanged. Clicking an annotation in the sidebar auto-expands its
 * enclosing collapsibles.
 */

interface SectionedBlockRendererProps {
  blocks: Block[];
  annotations: Annotation[];
  selectedAnnotationId: string | null;
  onSelectAnnotation?: (id: string) => void;
  onQuickAnnotate?: (
    blockId: string,
    originalText: string,
    annotationText: string,
  ) => void;
}

interface H2Group {
  heading: string;
  headingBlock: Block;
  blocks: Block[];
}

interface TaskGroup {
  number: number;
  title: string;
  /** null when this group holds prelude blocks that appeared before the first `### Task N:` heading. */
  headingBlock: Block | null;
  blocks: Block[];
}

interface FieldGroup {
  label: string;
  blocks: Block[];
}

const SECTIONS_DEFAULT_OPEN = new Set(["Summary", "Problem Statement"]);
const FIELD_DEFAULT_OPEN = new Set<string>();

function groupByH2(blocks: Block[]): H2Group[] {
  const groups: H2Group[] = [];
  let current: H2Group | null = null;
  for (const block of blocks) {
    if (block.type === "heading" && block.level === 2) {
      if (current) groups.push(current);
      // Include the heading block in the group so annotations anchored to the
      // heading still render and can be located by selectedAnnotationId.
      current = { heading: block.content, headingBlock: block, blocks: [block] };
    } else if (current) {
      current.blocks.push(block);
    } else {
      current = { heading: "", headingBlock: block, blocks: [block] };
    }
  }
  if (current) groups.push(current);
  return groups.filter((g) => g.heading || g.blocks.length > 0);
}

function groupByTaskH3(blocks: Block[]): TaskGroup[] {
  const groups: TaskGroup[] = [];
  let current: TaskGroup | null = null;
  const prelude: Block[] = [];
  for (const block of blocks) {
    if (block.type === "heading" && block.level === 3) {
      const m = block.content.match(/^Task\s+(\d+):\s*(.+)$/);
      if (m) {
        if (current) groups.push(current);
        // Flush any blocks that appeared before the first `### Task N:` match
        // into a prelude group (number=0, no headingBlock) so they aren't lost.
        else if (prelude.length > 0) {
          groups.push({ number: 0, title: "", headingBlock: null, blocks: prelude.splice(0) });
        }
        current = {
          number: parseInt(m[1], 10),
          title: m[2].trim(),
          headingBlock: block,
          blocks: [block],
        };
        continue;
      }
    }
    if (current) current.blocks.push(block);
    else prelude.push(block);
  }
  if (current) groups.push(current);
  else if (prelude.length > 0) {
    groups.push({ number: 0, title: "", headingBlock: null, blocks: prelude });
  }
  return groups;
}

function matchLabelMarker(block: Block): string | null {
  if (block.type !== "paragraph") return null;
  const m = block.content.match(/^\*\*([A-Za-z][A-Za-z0-9 /]+):\*\*\s*(.*)$/s);
  if (!m) return null;
  return m[1].trim();
}

function groupByLabel(blocks: Block[]): FieldGroup[] {
  const groups: FieldGroup[] = [];
  let current: FieldGroup | null = null;
  for (const block of blocks) {
    const label = matchLabelMarker(block);
    if (label) {
      if (current) groups.push(current);
      current = { label, blocks: [block] };
      continue;
    }
    if (current) current.blocks.push(block);
    else current = { label: "Notes", blocks: [block] };
  }
  if (current) groups.push(current);
  return groups;
}

interface CollapsibleCardProps {
  title: React.ReactNode;
  defaultOpen: boolean;
  expanded?: boolean;
  rightSlot?: React.ReactNode;
  children: React.ReactNode;
}

function CollapsibleCard({
  title,
  defaultOpen,
  expanded,
  rightSlot,
  children,
}: CollapsibleCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const isOpen = expanded ?? open;
  const setIsOpen = (next: boolean) => setOpen(next);
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2.5 px-4 py-3 text-left cursor-pointer hover:bg-muted/50 transition-colors"
      >
        <div className="flex-1 text-sm font-semibold">{title}</div>
        {rightSlot}
        <ChevronDown
          size={14}
          className={cn(
            "text-muted-foreground/60 transition-transform duration-200",
            isOpen ? "rotate-180" : "",
          )}
        />
      </button>
      {isOpen && (
        <div className="px-4 pb-4 pt-0 border-t border-border/50">
          <div className="pt-3">{children}</div>
        </div>
      )}
    </div>
  );
}

export function SectionedBlockRenderer({
  blocks,
  annotations,
  selectedAnnotationId,
  onSelectAnnotation,
  onQuickAnnotate,
}: SectionedBlockRendererProps) {
  const sections = useMemo(() => groupByH2(blocks), [blocks]);

  const [forceOpenBlockId, setForceOpenBlockId] = useState<string | null>(null);
  useEffect(() => {
    if (!selectedAnnotationId) {
      setForceOpenBlockId(null);
      return;
    }
    const ann = annotations.find((a) => a.id === selectedAnnotationId);
    setForceOpenBlockId(ann?.blockId ?? null);
  }, [selectedAnnotationId, annotations]);

  const renderLeaf = (groupBlocks: Block[]) => (
    <BlockRenderer
      blocks={groupBlocks}
      annotations={annotations}
      selectedAnnotationId={selectedAnnotationId}
      onSelectAnnotation={onSelectAnnotation}
      onQuickAnnotate={onQuickAnnotate}
    />
  );

  const containsBlock = (
    groupBlocks: Block[],
    targetId: string | null,
  ): boolean => !!targetId && groupBlocks.some((b) => b.id === targetId);

  return (
    <div className="space-y-2">
      {sections.map((section) => {
        const isTaskSection =
          section.heading === "Implementation Tasks" ||
          section.heading === "Tasks";
        const sectionDefaultOpen =
          !section.heading || SECTIONS_DEFAULT_OPEN.has(section.heading);
        const sectionForceOpen = containsBlock(section.blocks, forceOpenBlockId);
        if (!section.heading) {
          return (
            <div key={`preamble-${section.headingBlock.id}`}>
              {renderLeaf(section.blocks)}
            </div>
          );
        }
        return (
          <CollapsibleCard
            key={section.headingBlock.id}
            title={section.heading}
            defaultOpen={sectionDefaultOpen || sectionForceOpen}
            expanded={sectionForceOpen || undefined}
          >
            {isTaskSection ? (
              <div className="space-y-2">
                {groupByTaskH3(section.blocks).map((task) => {
                  const taskForceOpen = containsBlock(
                    task.blocks,
                    forceOpenBlockId,
                  );
                  // Prelude group (no heading) renders as a section without its own card.
                  if (task.headingBlock === null) {
                    return (
                      <div key={`prelude-${task.blocks[0]?.id ?? "empty"}`}>
                        {renderLeaf(task.blocks)}
                      </div>
                    );
                  }
                  const taskHeadingId = task.headingBlock.id;
                  return (
                    <CollapsibleCard
                      key={taskHeadingId}
                      title={
                        <div className="flex items-baseline gap-2">
                          <span className="text-xs font-mono text-muted-foreground/70">
                            Task {task.number}
                          </span>
                          <span>{task.title}</span>
                        </div>
                      }
                      defaultOpen={taskForceOpen}
                      expanded={taskForceOpen || undefined}
                    >
                      <div className="space-y-2">
                        {groupByLabel(task.blocks).map((field) => {
                          const fieldForceOpen = containsBlock(
                            field.blocks,
                            forceOpenBlockId,
                          );
                          return (
                            <CollapsibleCard
                              key={`${taskHeadingId}-${field.label}`}
                              title={
                                <span className="text-xs font-medium text-muted-foreground">
                                  {field.label}
                                </span>
                              }
                              defaultOpen={
                                FIELD_DEFAULT_OPEN.has(field.label) || fieldForceOpen
                              }
                              expanded={fieldForceOpen || undefined}
                            >
                              {renderLeaf(field.blocks)}
                            </CollapsibleCard>
                          );
                        })}
                      </div>
                    </CollapsibleCard>
                  );
                })}
              </div>
            ) : (
              renderLeaf(section.blocks)
            )}
          </CollapsibleCard>
        );
      })}
    </div>
  );
}
