import DOMPurify from "dompurify";

/** Renders one diagram's source to SVG markup; mermaid in the page, a stub in tests. */
export type RenderDiagram = (id: string, source: string) => Promise<string>;

/** The page's token by name, or "" when it has none. */
type Token = (name: string) => string;

/** The colours a diagram is drawn in, from the page's own tokens (dark or light), as the App draws its own. */
export function mermaidThemeVariables(token: Token) {
  const of = (name: string, fallback: string) => token(name) || fallback;
  return {
    fontSize: "14px",
    background: of("--ql-bg-sunken", "#fafafa"),
    primaryColor: of("--ql-surface", "#ffffff"),
    primaryTextColor: of("--ql-text", "#171717"),
    primaryBorderColor: of("--ql-border-strong", "#a8a8a8"),
    lineColor: of("--ql-text-muted", "#4d4d4d"),
    secondaryColor: of("--ql-surface-2", "#f2f2f2"),
    tertiaryColor: of("--ql-bg-sunken", "#fafafa"),
    noteBkgColor: of("--ql-surface-2", "#f2f2f2"),
    noteTextColor: of("--ql-text", "#171717"),
    edgeLabelBackground: of("--ql-bg-sunken", "#fafafa"),
  };
}

const pageToken: Token = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/** Mermaid, loaded only when a plan has a diagram, and strict: no clicks, no HTML labels, no scripts. */
export const mermaidRenderer = (): RenderDiagram => {
  let ready: Promise<typeof import("mermaid").default> | null = null;
  return async (id, source) => {
    const mermaid = await (ready ??= import("mermaid").then(({ default: m }) => m));
    // Drawn with the tokens as they are now, so a page that changed theme draws the next diagram in it.
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      // A diagram that does not parse keeps its source; mermaid draws no error graphic into the page.
      suppressErrorRendering: true,
      theme: "base",
      fontFamily: "Geist, system-ui, sans-serif",
      // SVG text labels: the sanitiser keeps SVG only, and HTML labels live in foreignObject.
      htmlLabels: false,
      flowchart: { useMaxWidth: false, htmlLabels: false },
      sequence: { useMaxWidth: false, wrap: true },
      themeVariables: mermaidThemeVariables(pageToken),
    });
    try {
      return (await mermaid.render(id, source)).svg;
    } finally {
      // Mermaid draws in a temporary element and leaves it behind when a diagram does not parse.
      document.getElementById(`d${id}`)?.remove();
      document.getElementById(id)?.remove();
    }
  };
};

const sanitizeSvg = (svg: string) => DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } });

/**
 * One diagram as sanitised SVG, or null when it does not parse or draws nothing: the page then
 * keeps the source, so the reader still sees what was meant.
 */
export async function drawDiagram(
  render: RenderDiagram,
  id: string,
  source: string,
  sanitize: (svg: string) => string = sanitizeSvg,
): Promise<string | null> {
  try {
    const svg = sanitize(await render(id, source));
    return svg.trim() === "" ? null : svg;
  } catch {
    return null;
  }
}
