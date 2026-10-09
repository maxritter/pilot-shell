// What the site knows of the App's MermaidBlock (see step-document.d.ts for why).
/** Where Mermaid comes from on a page that is not the App: the site bundles it, loaded when a diagram is drawn. */
export function loadMermaidFrom(load: () => Promise<typeof import("mermaid")>): void;
