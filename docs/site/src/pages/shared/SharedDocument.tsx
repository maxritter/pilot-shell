import { useCallback, type ReactNode } from "react";
import type { StepComment } from "@ql/ui/steps/StepDocument";
import { loadMermaidFrom } from "@ql/ui/reader/MermaidBlock";
import { StepDocument } from "@ql/ui/steps/StepDocument";
import { useTheme } from "@/hooks/useTheme";
import { mockupHtml, withoutShownMockups } from "@/lib/sharing/plan";

// A shared document is drawn by the App's own Reader, so it looks the same here as in the App's step
// page and its Files tab: Sections and Copy at the top, diagrams, comments under their passages.
// The App loads Mermaid from a file of its own; here it is part of this site's build, fetched only
// when a document has a diagram (the page's policy allows scripts from this origin only).
loadMermaidFrom(() => import("mermaid"));

const NOT_IN_LINK = "The mockup is not part of this link. Ask for a new link to see it.";

type Props = {
  /** The document's name in the link: what Sections names as its path, and what a comment is filed under. */
  name: string;
  markdown: string;
  /** Everything the link carries, for the mockups a document names. */
  docs: Record<string, string>;
  /** The comments on this document's passages. */
  comments: StepComment[];
  /** A person asked to comment on this passage. */
  onQuote: (quote: string) => void;
  /** Beside Sections and Copy, at the top of the document. */
  extraTools?: ReactNode;
  /** Mockups already drawn elsewhere on the page, so none is drawn twice. */
  shown?: ReadonlySet<string>;
};

export function SharedDocument({ name, markdown, docs, comments, onQuote, extraTools, shown }: Props) {
  const { theme } = useTheme();
  const loadArtifact = useCallback(
    (file: string) => {
      const html = mockupHtml(docs, file);
      return html === undefined ? Promise.reject(new Error(NOT_IN_LINK)) : Promise.resolve(html);
    },
    [docs],
  );
  return (
    <StepDocument
      path={name}
      markdown={shown === undefined ? markdown : withoutShownMockups(markdown, shown)}
      comments={comments}
      sections={null}
      theme={theme}
      loadArtifact={loadArtifact}
      onQuote={onQuote}
      extraTools={extraTools}
    />
  );
}
