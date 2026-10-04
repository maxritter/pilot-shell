import { mockupHtml, mockupName, type PlanBlock } from "@/lib/sharing/plan";
import { Diagram } from "./Diagram";
import { MissingMockup, MockupFrame } from "./Frame";

/**
 * The plan's parts in reading order: text, then each diagram and mockup where the plan put it.
 * `shown` names mockups already drawn elsewhere on the page (under a question), so none is drawn twice.
 */
export function Blocks({ blocks, docs, shown }: { blocks: PlanBlock[]; docs: Record<string, string>; shown?: ReadonlySet<string> }) {
  return (
    <>
      {blocks.map((block) => {
        if (block.kind === "html") {
          return (
            <div
              key={block.key}
              className="sh-doc typeset typeset-plan"
              // The markdown is sanitised in plan.ts (or escaped when there is no DOM).
              // biome-ignore lint/security/noDangerouslySetInnerHTML: sanitised by htmlOf
              dangerouslySetInnerHTML={{ __html: block.html }}
            />
          );
        }
        if (block.kind === "mermaid") return <Diagram key={block.key} source={block.source} />;
        if (shown?.has(mockupName(block.path))) return null;
        const html = mockupHtml(docs, block.path);
        return html === undefined ? <MissingMockup key={block.key} /> : <MockupFrame key={block.key} html={html} title="Mockup" />;
      })}
    </>
  );
}
