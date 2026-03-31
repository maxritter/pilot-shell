import type { Block } from "./types";

let blockIdCounter = 0;

function nextId(): string {
  return `block-${blockIdCounter++}`;
}

/**
 * Splits a markdown string into a flat array of Block objects for annotation rendering.
 * Each block is an independently annotatable unit with a stable DOM anchor.
 * Ported from console/src/ui/viewer/views/Spec/annotation/parser.ts
 */
export function parseMarkdownToBlocks(markdown: string): Block[] {
  blockIdCounter = 0;
  const blocks: Block[] = [];
  const lines = markdown.split("\n");
  let i = 0;
  let order = 0;

  const flush = (
    type: Block["type"],
    content: string,
    startLine: number,
    extra?: Partial<Block>,
  ) => {
    if (!content && type !== "hr") return;
    blocks.push({ id: nextId(), type, content, order: order++, startLine, ...extra });
  };

  let paragraphBuffer: string[] = [];
  let paragraphStartLine = 1;

  const flushParagraph = () => {
    if (paragraphBuffer.length > 0) {
      flush("paragraph", paragraphBuffer.join("\n"), paragraphStartLine);
      paragraphBuffer = [];
    }
  };

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();
    const lineNum = i + 1;

    if (trimmed.startsWith("#")) {
      flushParagraph();
      const level = (trimmed.match(/^#+/) ?? [""])[0].length;
      flush("heading", trimmed.replace(/^#+\s*/, ""), lineNum, { level });
      i++; continue;
    }

    if (trimmed === "---" || trimmed === "***" || trimmed === "___") {
      flushParagraph();
      flush("hr", "", lineNum);
      i++; continue;
    }

    if (trimmed.startsWith("```")) {
      flushParagraph();
      const fenceLen = (trimmed.match(/^`+/) ?? ["```"])[0].length;
      const closingFence = new RegExp(`^\`{${fenceLen},}\\s*$`);
      const language = trimmed.slice(fenceLen).trim() || undefined;
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !closingFence.test(lines[i].trim())) {
        codeLines.push(lines[i]);
        i++;
      }
      flush("code", codeLines.join("\n"), lineNum, { language });
      i++; continue;
    }

    if (trimmed.startsWith(">")) {
      flushParagraph();
      flush("blockquote", trimmed.replace(/^>\s*/, ""), lineNum);
      i++; continue;
    }

    if (trimmed.match(/^(\*|-|\d+\.)\s/)) {
      flushParagraph();
      const leadingSpaces = line.match(/^(\s*)/)?.[1] ?? "";
      const spaceCount = leadingSpaces.replace(/\t/g, "  ").length;
      const level = Math.floor(spaceCount / 2);
      let content = trimmed.replace(/^(\*|-|\d+\.)\s/, "");
      let checked: boolean | undefined;
      const checkboxMatch = content.match(/^\[([ xX])\]\s*/);
      if (checkboxMatch) {
        checked = checkboxMatch[1].toLowerCase() === "x";
        content = content.replace(/^\[([ xX])\]\s*/, "");
      }
      flush("list-item", content, lineNum, { level, checked });
      i++; continue;
    }

    if (trimmed.startsWith("|")) {
      flushParagraph();
      const tableLines: string[] = [line];
      const tableStartLine = lineNum;
      i++;
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      flush("table", tableLines.join("\n"), tableStartLine);
      continue;
    }

    if (trimmed === "") {
      flushParagraph();
      i++; continue;
    }

    if (paragraphBuffer.length === 0) paragraphStartLine = lineNum;
    paragraphBuffer.push(line);
    i++;
  }

  flushParagraph();
  return blocks;
}
