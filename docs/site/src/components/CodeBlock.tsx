import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CodeBlockProps {
  command: string;
  /** Accessible name for what is being copied, e.g. "install command". */
  label?: string;
}

/** One-line shell command with a copy button, per the design system's CodeBlock. */
const CodeBlock = ({ command, label = "command" }: CodeBlockProps) => {
  const [copyState, setCopyState] = useState<"idle" | "copied" | "error">("idle");

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopyState("copied");
      setTimeout(() => setCopyState("idle"), 2000);
    } catch {
      setCopyState("error");
    }
  };

  return (
    <div className="bg-background/60 rounded-lg p-3 font-mono text-sm border border-border/50">
      <div className="flex items-center justify-between gap-3">
        <code
          className="text-muted-foreground text-xs sm:text-sm whitespace-nowrap overflow-x-auto"
          tabIndex={0}
        >
          <span className="text-primary">$</span> {command}
        </code>
        <Button
          variant="secondary"
          size="sm"
          onClick={copyToClipboard}
          className="flex-shrink-0 min-h-11 min-w-11 px-3"
          aria-label={
            copyState === "copied"
              ? `${label} copied`
              : copyState === "error"
                ? `Retry copying ${label}`
                : `Copy ${label}`
          }
        >
          {copyState === "copied" ? (
            <>
              <Check className="h-3.5 w-3.5 text-primary mr-1.5" />
              <span className="text-xs">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5 mr-1.5" />
              <span className="text-xs">
                {copyState === "error" ? "Copy failed" : "Copy"}
              </span>
            </>
          )}
        </Button>
      </div>
      <span className="sr-only" role="status" aria-live="polite">
        {copyState === "copied"
          ? `${label} copied to clipboard.`
          : copyState === "error"
            ? `Could not copy the ${label}. Select and copy it manually.`
            : ""}
      </span>
    </div>
  );
};

export default CodeBlock;
