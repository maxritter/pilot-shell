import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { PendingSelection } from "@/lib/annotation/types";

interface AnnotationToolbarProps {
  selection: PendingSelection;
  onSubmit: (text: string) => void;
  onDismiss: () => void;
}

/**
 * Floating popover that appears at the text selection position.
 * Dismisses on Escape or click outside.
 */
export function AnnotationToolbar({ selection, onSubmit, onDismiss }: AnnotationToolbarProps) {
  const popoverRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [text, setText] = useState("");

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onDismiss();
    };
    const handleMouseDown = (e: MouseEvent) => {
      requestAnimationFrame(() => {
        if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
          onDismiss();
        }
      });
    };
    document.addEventListener("keydown", handleKey);
    document.addEventListener("mousedown", handleMouseDown);
    return () => {
      document.removeEventListener("keydown", handleKey);
      document.removeEventListener("mousedown", handleMouseDown);
    };
  }, [onDismiss]);

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const top = selection.rect.top - 108;
  const left = selection.rect.left + selection.rect.width / 2;

  return (
    <div
      ref={popoverRef}
      style={{
        position: "fixed",
        top: Math.max(top, 8),
        left,
        transform: "translateX(-50%)",
        zIndex: 50,
        width: 260,
      }}
      onMouseDown={(e) => e.stopPropagation()}
    >
      <Card className="p-2.5 shadow-lg space-y-2">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Add annotation… (Enter to save)"
          rows={2}
          className="w-full text-xs resize-none rounded border border-input bg-background px-2 py-1.5 placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <div className="flex gap-1 justify-end">
          <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={onDismiss}>
            Cancel
          </Button>
          <Button size="sm" className="h-6 text-xs" disabled={!text.trim()} onClick={handleSubmit}>
            Save
          </Button>
        </div>
      </Card>
    </div>
  );
}
