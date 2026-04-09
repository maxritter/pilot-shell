import { useState } from "react";
import { Send, ChevronRight, ChevronDown, MessageSquarePlus, X, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Annotation } from "@/lib/annotation/types";

interface FeedbackSidebarProps {
  /** Original annotations from the sharer (read-only) */
  sharerAnnotations: Annotation[];
  /** Recipient's own new annotations (editable) */
  recipientAnnotations: Annotation[];
  /** Display name for feedback attribution */
  authorName: string;
  onAuthorNameChange: (name: string) => void;
  onRemoveAnnotation: (id: string) => void;
  onUpdateAnnotation: (id: string, text: string) => void;
  onSendFeedback: () => void;
  isSending?: boolean;
}

export function FeedbackSidebar({
  sharerAnnotations,
  recipientAnnotations,
  authorName,
  onAuthorNameChange,
  onRemoveAnnotation,
  onUpdateAnnotation,
  onSendFeedback,
  isSending = false,
}: FeedbackSidebarProps) {
  const [sharerExpanded, setSharerExpanded] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  return (
    <div className="flex flex-col h-full border-l border-border bg-muted/20">
      {/* Header */}
      <div className="px-3 py-2.5 border-b border-border flex-shrink-0 space-y-2.5">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold flex-1">Feedback</span>
          {recipientAnnotations.length > 0 && (
            <Badge variant="default" className="text-[10px] h-4 px-1.5">
              {recipientAnnotations.length}
            </Badge>
          )}
        </div>

        {/* Author name input */}
        <div>
          <label className="text-[10px] text-muted-foreground block mb-1">Your name</label>
          <input
            type="text"
            value={authorName}
            onChange={(e) => onAuthorNameChange(e.target.value)}
            placeholder="Anonymous"
            className="w-full text-xs rounded border border-input bg-background px-2 py-1 placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        {/* Send button */}
        <Button
          className="w-full gap-2 h-8 text-xs"
          disabled={recipientAnnotations.length === 0 || isSending}
          onClick={onSendFeedback}
        >
          {isSending ? (
            <span className="h-3 w-3 border border-current border-t-transparent rounded-full animate-spin" />
          ) : (
            <Send size={13} />
          )}
          Send Feedback ({recipientAnnotations.length})
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {/* Sharer's annotations (read-only, collapsed) */}
        {sharerAnnotations.length > 0 && (
          <div>
            <button
              className="flex items-center gap-1.5 w-full text-left py-1 px-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
              aria-label={sharerExpanded ? "Collapse original annotations" : "Expand original annotations"}
              onClick={() => setSharerExpanded(!sharerExpanded)}
            >
              {sharerExpanded
                ? <ChevronDown size={12} />
                : <ChevronRight size={12} />
              }
              <span>{sharerAnnotations.length} original annotation{sharerAnnotations.length !== 1 ? "s" : ""}</span>
            </button>
            {sharerExpanded && (
              <div className="space-y-1 mt-1 ml-2">
                {sharerAnnotations.map((ann, i) => (
                  <div
                    key={ann.id}
                    className="flex items-start gap-2 p-2 rounded-lg bg-muted/50 border border-border/50"
                  >
                    <span className="inline-flex items-center justify-center text-[10px] font-bold rounded-full w-4 h-4 flex-shrink-0 mt-0.5 bg-muted-foreground/20 text-muted-foreground">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      {ann.originalText && (
                        <p className="text-[11px] text-muted-foreground italic break-words mb-0.5">
                          &ldquo;{ann.originalText.slice(0, 50)}{ann.originalText.length > 50 ? "…" : ""}&rdquo;
                        </p>
                      )}
                      <p className="text-xs text-foreground/70 break-words">{ann.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Recipient's feedback */}
        <div>
          <p className="text-xs font-medium text-muted-foreground px-1 mb-1">Your Feedback</p>
          {recipientAnnotations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center px-3">
              <MessageSquarePlus size={24} className="text-muted-foreground/30 mb-2" />
              <p className="text-xs text-muted-foreground/60 mb-1">No annotations yet</p>
              <p className="text-[10px] text-muted-foreground/40 leading-relaxed">
                Hover over a block and click the + button to add a note.
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {recipientAnnotations.map((ann, i) => {
                const isEditing = editingId === ann.id;
                if (isEditing) {
                  return (
                    <div key={ann.id} className="p-2.5 rounded-lg border border-border bg-muted/30 space-y-2">
                      {ann.originalText && (
                        <p className="text-[11px] text-muted-foreground italic break-words">
                          &ldquo;{ann.originalText.slice(0, 80)}{ann.originalText.length > 80 ? "…" : ""}&rdquo;
                        </p>
                      )}
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        rows={2}
                        autoFocus
                        className="w-full text-xs resize-none rounded border border-input bg-background px-2 py-1.5 placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                        placeholder="Your feedback…"
                      />
                      <div className="flex gap-1 items-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 text-xs text-destructive hover:text-destructive"
                          onClick={() => { setEditingId(null); onRemoveAnnotation(ann.id); }}
                        >
                          <Trash2 size={11} />
                        </Button>
                        <div className="flex gap-1 ml-auto">
                          <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => setEditingId(null)}>
                            Cancel
                          </Button>
                          <Button
                            size="sm"
                            className="h-6 text-xs"
                            disabled={editText === ann.text}
                            onClick={() => { onUpdateAnnotation(ann.id, editText); setEditingId(null); }}
                          >
                            Save
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                }
                return (
                  <div
                    key={ann.id}
                    className={cn(
                      "flex items-start gap-2 p-2 rounded-lg cursor-pointer group transition-colors border border-transparent",
                      "hover:bg-muted/40"
                    )}
                    onClick={() => { setEditingId(ann.id); setEditText(ann.text); }}
                  >
                    <span className="inline-flex items-center justify-center text-[10px] font-bold rounded-full w-4 h-4 flex-shrink-0 mt-0.5 bg-primary/20 text-primary">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      {ann.originalText && (
                        <p className="text-[11px] text-muted-foreground italic break-words mb-0.5">
                          &ldquo;{ann.originalText.slice(0, 50)}{ann.originalText.length > 50 ? "…" : ""}&rdquo;
                        </p>
                      )}
                      <p className="text-xs text-foreground/80 break-words">
                        {ann.text.slice(0, 100)}{ann.text.length > 100 ? "…" : ""}
                      </p>
                    </div>
                    <button
                      className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 text-muted-foreground hover:text-destructive p-0.5"
                      aria-label={`Remove annotation ${i + 1}`}
                      onClick={(e) => { e.stopPropagation(); onRemoveAnnotation(ann.id); }}
                    >
                      <X size={11} />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
