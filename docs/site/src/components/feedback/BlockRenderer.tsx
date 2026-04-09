import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Annotation, Block } from "@/lib/annotation/types";

interface BlockRendererProps {
  blocks: Block[];
  annotations: Annotation[];
  selectedAnnotationId: string | null;
  onSelectAnnotation?: (id: string) => void;
  onQuickAnnotate?: (blockId: string, originalText: string, annotationText: string) => void;
}

function blockToMarkdown(block: Block): string {
  switch (block.type) {
    case "heading":
      return `${"#".repeat(block.level ?? 2)} ${block.content}`;
    case "code":
      return `\`\`\`${block.language ?? ""}\n${block.content}\n\`\`\``;
    case "blockquote":
      return `> ${block.content}`;
    case "list-item": {
      const indent = block.level ? "  ".repeat(block.level) : "";
      const checkbox = block.checked === true ? "[x] " : block.checked === false ? "[ ] " : "";
      return `${indent}- ${checkbox}${block.content}`;
    }
    case "table":
      return block.content;
    case "hr":
      return "---";
    default:
      return block.content;
  }
}

const BlockItem = function BlockItem({
  block,
  blockAnnotations,
  allAnnotations,
  selectedAnnotationId,
  onSelectAnnotation,
  onQuickAnnotate,
}: {
  block: Block;
  blockAnnotations: Annotation[];
  allAnnotations: Annotation[];
  selectedAnnotationId: string | null;
  onSelectAnnotation?: (id: string) => void;
  onQuickAnnotate?: (blockId: string, originalText: string, annotationText: string) => void;
}) {
  const md = blockToMarkdown(block);
  const [showQuickInput, setShowQuickInput] = useState(false);
  const [quickText, setQuickText] = useState("");

  const handleQuickSubmit = () => {
    if (quickText.trim() && onQuickAnnotate) {
      onQuickAnnotate(block.id, block.content.slice(0, 80), quickText.trim());
    }
    setQuickText("");
    setShowQuickInput(false);
  };

  return (
    <div
      data-block-id={block.id}
      data-block-type={block.type}
      className="annotation-block group/block relative"
      style={{ overflowWrap: "break-word", wordBreak: "break-word", maxWidth: "100%" }}
    >
      {onQuickAnnotate && !showQuickInput && (
        <button
          className="absolute -left-7 top-0.5 w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center opacity-0 group-hover/block:opacity-100 transition-opacity hover:bg-primary/20 z-10"
          title="Add annotation to this block"
          onClick={(e) => { e.stopPropagation(); setShowQuickInput(true); }}
        >
          <Plus size={12} />
        </button>
      )}

      {showQuickInput && (
        <div className="mb-2 p-2 rounded-lg border border-primary/30 bg-muted/50 space-y-1.5">
          <p className="text-[10px] text-muted-foreground italic truncate">
            Block: &ldquo;{block.content.slice(0, 60)}{block.content.length > 60 ? "…" : ""}&rdquo;
          </p>
          <textarea
            autoFocus
            rows={2}
            value={quickText}
            onChange={(e) => setQuickText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleQuickSubmit(); }
              if (e.key === "Escape") { setShowQuickInput(false); setQuickText(""); }
            }}
            className="w-full text-xs resize-none rounded border border-input bg-background px-2 py-1.5 placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Your annotation… (Enter to save, Esc to cancel)"
          />
          <div className="flex gap-1 justify-end">
            <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => { setShowQuickInput(false); setQuickText(""); }}>
              Cancel
            </Button>
            <Button size="sm" className="h-6 text-xs" disabled={!quickText.trim()} onClick={handleQuickSubmit}>
              Save
            </Button>
          </div>
        </div>
      )}

      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="text-xl font-semibold mt-6 mb-3 scroll-mt-4">{children}</h1>,
          h2: ({ children }) => <h2 className="text-lg font-semibold mt-6 mb-3 pb-2 border-b border-border scroll-mt-4">{children}</h2>,
          h3: ({ children }) => <h3 className="text-base font-semibold mt-4 mb-2 scroll-mt-4">{children}</h3>,
          h4: ({ children }) => <h4 className="text-sm font-medium mt-3 mb-1">{children}</h4>,
          h5: ({ children }) => <h5 className="text-sm font-medium mt-3 mb-1">{children}</h5>,
          h6: ({ children }) => <h6 className="text-sm font-medium mt-3 mb-1">{children}</h6>,
          p: ({ children }) => <p className="text-sm text-foreground/80 mb-3 leading-relaxed" style={{ overflowWrap: "break-word" }}>{children}</p>,
          ul: ({ children }) => <ul className="text-sm space-y-1.5 mb-4 ml-1">{children}</ul>,
          ol: ({ children }) => <ol className="text-sm space-y-1.5 mb-4 ml-1 list-decimal list-inside">{children}</ol>,
          li: ({ children }) => (
            <li className="text-foreground/80 flex items-start gap-2">
              <span className="text-primary mt-0.5 text-xs select-none">&#9656;</span>
              <span className="flex-1">{children}</span>
            </li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary/50 pl-4 py-1 my-3 text-sm text-foreground/70 italic">{children}</blockquote>
          ),
          code: ({ className, children }) => {
            const isInline = !className;
            if (isInline) {
              return <code className="bg-muted text-primary px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>;
            }
            return <code className="block bg-muted p-3 rounded-lg text-xs font-mono overflow-x-auto mb-4 border border-border/50">{children}</code>;
          },
          pre: ({ children }) => (
            <pre className="bg-muted p-3 rounded-lg text-xs font-mono mb-4 border border-border/50" style={{ whiteSpace: "pre-wrap", overflowWrap: "break-word" }}>{children}</pre>
          ),
          strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4"><table className="w-full text-sm border-collapse">{children}</table></div>
          ),
          thead: ({ children }) => <thead className="bg-muted">{children}</thead>,
          th: ({ children }) => <th className="text-left text-xs font-medium text-muted-foreground p-2 border border-border/50">{children}</th>,
          td: ({ children }) => <td className="text-sm p-2 border border-border/50">{children}</td>,
          hr: () => <hr className="my-6 border-border" />,
          input: ({ checked, ...props }) => (
            <input {...props} checked={checked} readOnly className="mt-0.5 h-3.5 w-3.5 accent-primary" />
          ),
        }}
      >
        {md}
      </Markdown>

      {blockAnnotations.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3 -mt-1">
          {blockAnnotations.map((ann) => {
            const globalIndex = allAnnotations.findIndex((a) => a.id === ann.id) + 1;
            const isSelected = ann.id === selectedAnnotationId;
            return (
              <button
                key={ann.id}
                className={cn(
                  "inline-flex items-center gap-1.5 text-[11px] px-2 py-0.5 rounded-full cursor-pointer transition-colors",
                  isSelected
                    ? "bg-primary text-primary-foreground font-bold"
                    : "bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-700/50"
                )}
                title={ann.text}
                onClick={(e) => { e.stopPropagation(); onSelectAnnotation?.(ann.id); }}
              >
                <span className={cn(
                  "inline-flex items-center justify-center text-[9px] font-bold rounded-full w-4 h-4",
                  isSelected ? "bg-primary-foreground/20" : "bg-blue-200/60 dark:bg-blue-700/40"
                )}>
                  {globalIndex}
                </span>
                <span className="truncate max-w-48">
                  &ldquo;{ann.originalText.slice(0, 40)}{ann.originalText.length > 40 ? "…" : ""}&rdquo;
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export function BlockRenderer({
  blocks,
  annotations,
  selectedAnnotationId,
  onSelectAnnotation,
  onQuickAnnotate,
}: BlockRendererProps) {
  return (
    <div
      className="annotation-content select-text pl-8"
      style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
    >
      {blocks.map((block) => (
        <BlockItem
          key={block.id}
          block={block}
          blockAnnotations={annotations.filter((a) => a.blockId === block.id)}
          allAnnotations={annotations}
          selectedAnnotationId={selectedAnnotationId}
          onSelectAnnotation={onSelectAnnotation}
          onQuickAnnotate={onQuickAnnotate}
        />
      ))}
    </div>
  );
}
