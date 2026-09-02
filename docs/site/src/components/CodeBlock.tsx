import { useState } from "react";
import { Check, Copy } from "lucide-react";

interface CodeBlockProps {
  command: string;
  /** Accessible name for what is being copied, e.g. "install command". */
  label?: string;
  /** Wrap the command over several lines instead of scrolling it horizontally. */
  wrap?: boolean;
}

/** One-line shell command in a square hairline shell with a copy button. */
const CodeBlock = ({ command, label = "command", wrap = false }: CodeBlockProps) => {
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
    <>
      <div className="ps-cmd" role="group" aria-label={label}>
        <code
          className={`ps-cmd-code overflow-x-auto${wrap ? " ps-wrap" : ""}`}
          tabIndex={0}
        >
          <span className="ps-brand-txt">$</span> {command}
        </code>
        <button
          type="button"
          onClick={copyToClipboard}
          className={`ps-btn ps-btn-sm ps-btn-sec ps-cmd-copy${copyState === "copied" ? " ps-copied" : ""}`}
          aria-label={
            copyState === "copied"
              ? `${label} copied`
              : copyState === "error"
                ? `Retry copying ${label}`
                : `Copy ${label}`
          }
        >
          {copyState === "copied" ? (
            <Check className="h-4 w-4" aria-hidden="true" />
          ) : (
            <Copy className="h-4 w-4" aria-hidden="true" />
          )}
          <span>{copyState === "copied" ? "Copied" : copyState === "error" ? "Copy failed" : "Copy"}</span>
        </button>
      </div>
      <span className="sr-only" role="status" aria-live="polite">
        {copyState === "copied"
          ? `${label} copied to clipboard.`
          : copyState === "error"
            ? `Could not copy the ${label}. Select and copy it manually.`
            : ""}
      </span>
    </>
  );
};

export default CodeBlock;
