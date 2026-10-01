import DOMPurify from "dompurify";

/** Renders one diagram's source to SVG markup; mermaid in the page, a stub in tests. */
export type RenderDiagram = (id: string, source: string) => Promise<string>;

type Block = { textContent: string | null; closest(selector: string): Element | null };
type Root = { querySelectorAll(selector: string): ArrayLike<Block> };

/** Mermaid, loaded only when a plan has a diagram, and strict: no clicks, no HTML labels, no scripts. */
export const mermaidRenderer = (dark: boolean): RenderDiagram => {
  let ready: Promise<typeof import("mermaid").default> | null = null;
  return async (id, source) => {
    ready ??= import("mermaid").then(({ default: mermaid }) => {
      // SVG text labels: the sanitiser keeps SVG only, and HTML labels live in foreignObject.
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        // A diagram that does not parse keeps its source; mermaid draws no error graphic into the page.
        suppressErrorRendering: true,
        theme: dark ? "dark" : "default",
        htmlLabels: false,
        flowchart: { htmlLabels: false },
      });
      return mermaid;
    });
    return (await (await ready).render(id, source)).svg;
  };
};

/**
 * Replaces each ```mermaid block of a rendered plan with its diagram. A diagram
 * that does not parse keeps its source, so the reader still sees what was meant.
 * Returns how many rendered.
 */
export async function renderDiagrams(
  root: Root,
  render: RenderDiagram,
  doc: Document = document,
  sanitize: (svg: string) => string = (svg) => DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } }),
): Promise<number> {
  const blocks = Array.from(root.querySelectorAll("pre > code.language-mermaid"));
  let rendered = 0;
  for (const [i, code] of blocks.entries()) {
    const pre = code.closest("pre");
    if (pre === null) continue;
    let svg: string;
    try {
      svg = await render(`sh-diagram-${i}`, code.textContent ?? "");
    } catch {
      continue;
    }
    const figure = doc.createElement("figure");
    figure.className = "sh-diagram";
    figure.innerHTML = sanitize(svg);
    pre.replaceWith(figure);
    rendered++;
  }
  return rendered;
}
