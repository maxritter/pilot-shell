import { describe, expect, it } from "vitest";
import { renderDiagrams } from "./diagrams";

/**
 * A shared plan's ```mermaid blocks become diagrams; one that does not parse keeps
 * its source. The page's DOM is faked: the test environment has none.
 */

type Fake = { tag: string; className: string; innerHTML: string; replacedBy?: Fake };

function page(sources: string[]) {
  const pres: Fake[] = sources.map(() => ({ tag: "pre", className: "", innerHTML: "" }));
  const codes = sources.map((text, i) => ({
    textContent: text,
    closest: (selector: string) => (selector === "pre" ? (pres[i] as unknown as Element) : null),
  }));
  for (const pre of pres) (pre as unknown as { replaceWith: (f: Fake) => void }).replaceWith = (f) => (pre.replacedBy = f);
  const root = {
    querySelectorAll: (selector: string) => (selector === "pre > code.language-mermaid" ? codes : []),
  };
  const doc = { createElement: (tag: string) => ({ tag, className: "", innerHTML: "" }) } as unknown as Document;
  return { root, pres, doc };
}

describe("diagrams on a shared plan", () => {
  it("replaces each mermaid block with its diagram, in order, under its own id", async () => {
    const { root, pres, doc } = page(["graph LR; A-->B", "graph TD; C-->D"]);
    const seen: string[] = [];
    const count = await renderDiagrams(
      root,
      async (id, source) => {
        seen.push(`${id}:${source}`);
        return `<svg id="${id}"><g/></svg>`;
      },
      doc,
      (svg) => svg.replace("<g/>", ""),
    );
    expect(count).toBe(2);
    expect(seen).toEqual(["sh-diagram-0:graph LR; A-->B", "sh-diagram-1:graph TD; C-->D"]);
    expect(pres.map((p) => p.replacedBy?.className)).toEqual(["sh-diagram", "sh-diagram"]);
    expect(pres[0]?.replacedBy?.tag).toBe("figure");
    // What goes on the page is the sanitised SVG, never the renderer's raw output.
    expect(pres[0]?.replacedBy?.innerHTML).toBe('<svg id="sh-diagram-0"></svg>');
  });

  it("keeps the source of a diagram that does not parse", async () => {
    const { root, pres, doc } = page(["graph LR; A-->B", "not a diagram"]);
    const count = await renderDiagrams(
      root,
      async (id, source) => {
        if (source === "not a diagram") throw new Error("Parse error");
        return `<svg id="${id}"/>`;
      },
      doc,
      (svg) => svg,
    );
    expect(count).toBe(1);
    expect(pres[0]?.replacedBy).toBeDefined();
    expect(pres[1]?.replacedBy).toBeUndefined();
  });
});
