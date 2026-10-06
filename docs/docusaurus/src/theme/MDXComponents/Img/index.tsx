import React, { type ReactNode } from "react";
import OriginalImg from "@theme-original/MDXComponents/Img";
import type { Props } from "@theme/MDXComponents/Img";

/** Keep the themed illustration in the article and let readers inspect its full-size source. */
export default function Img(props: Props): ReactNode {
  const src = typeof props.src === "string" ? props.src : "";
  if (!src.includes("/img/diagrams/")) return <OriginalImg {...props} />;
  const theme = /-dark\.(svg|png)$/.test(src) ? "dark" : "light";
  return (
    <a className="ql-diagram" data-illustration-theme={theme} href={src} target="_blank" rel="noopener noreferrer" aria-label={`Open illustration full size: ${props.alt ?? "Diagram"}`}>
      <OriginalImg {...props} />
      <span className="ql-diagram-open">Open full size ↗</span>
    </a>
  );
}
