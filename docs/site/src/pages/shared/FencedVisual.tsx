import { panelNodes, parseFence, SURFACES, type FragmentKind } from "@ql/core/docs/fragments";
import { VisualLegend } from "@ql/ui/reader/VisualLegend";
import { fencePage } from "@ql/core/docs/fence-page";
import wireCSS from "@ql/ui/reader/wire.css?inline";
import panelCSS from "@ql/ui/reader/panel.css?inline";

const HEIGHTS: Record<string, number> = { browser: 560, desktop: 560, phone: 760, popover: 320, panel: 480 };

/** Shared visuals have no script channel, navigation or automatic resize. */
export function FencedVisual({ kind, source, theme = "light", onComment }: { kind: FragmentKind; source: string; theme?: string; onComment?: (quote: string) => void }) {
  const parsed = parseFence(kind, source);
  if (parsed.fragment === "") return (
    <div className="visual-error" role="note">
      <p>This {kind} could not be drawn: {parsed.errors.map((error) => `line ${error.line}: ${error.message}`).join("; ")}</p>
      <pre><code>{source}</code></pre>
    </div>
  );
  const surface = kind === "panel" ? "panel" : parsed.header.surface;
  const title = parsed.header.title || parsed.header.name || kind;
  const html = fencePage(kind, source, theme, { wire: wireCSS, panel: panelCSS })!;
  return (
    <figure className="visual fenced-visual" data-testid={`shared-${kind}`} style={{ margin: "16px 0" }}>
      <figcaption className="visual-bar" style={{ flexWrap: "wrap" }}>
        <span>{kind} · {title} · {kind === "panel" ? parsed.header.lens : surface}</span>
        <span className="visual-spacer" />
        <span>drawn without scripts · fixed height {HEIGHTS[surface]} px</span>
      </figcaption>
      <iframe title={title} sandbox="" referrerPolicy="no-referrer" srcDoc={html} style={{ display: "block", border: 0, width: "100%", maxWidth: kind === "panel" ? undefined : SURFACES[surface], height: HEIGHTS[surface] }} />
      {kind === "panel" ? <VisualLegend marks={panelNodes(parsed.fragment).flatMap((node) => node.marks)} /> : null}
      {onComment !== undefined ? <div className="visual-bar" style={{ flexWrap: "wrap" }}>
        <button type="button" className="q-link" style={{ minHeight: 44 }} onClick={() => onComment(`${kind} ${parsed.header.name ?? kind}`)}>Give feedback on this {kind}</button>
        <span>feedback here is on the whole {kind}</span>
      </div> : null}
    </figure>
  );
}
