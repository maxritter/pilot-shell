import React, { type ReactNode } from "react";
import OriginalImg from "@theme-original/MDXComponents/Img";
import type { Props } from "@theme/MDXComponents/Img";

/** Keep the themed illustration in the article and let readers inspect its full-size source. */
export default function Img(props: Props): ReactNode {
  const src = typeof props.src === "string" ? props.src : "";
  const drawing = src.includes("/img/diagrams/");
  const screenshot = src.includes("/img/app/");
  if (!drawing && !screenshot) return <OriginalImg {...props} />;
  const theme = /-dark\.(svg|png|webp)$/.test(src) ? "dark" : "light";
  // App screenshots are 2240 by 1800 (56:45); the hidden theme's copy loads only when it is shown.
  const extra = screenshot ? { loading: "lazy" as const, decoding: "async" as const, width: 2240, height: 1800 } : {};
  return (
    <a className="ql-diagram" data-illustration-theme={theme} href={src} target="_blank" rel="noopener noreferrer" aria-label={`Open illustration full size: ${props.alt ?? "Diagram"}`}>
      <OriginalImg {...extra} {...props} />
      <span className="ql-diagram-open">Open full size ↗</span>
    </a>
  );
}
