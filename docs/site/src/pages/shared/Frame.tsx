import { useCallback, useEffect, useRef, useState } from "react";
import { withCsp } from "@/lib/sharing/plan";
import type { PlanStill } from "@/lib/sharing/sharing";

/**
 * A mockup the agent wrote, shown the way the App shows it: a page of its own in a sandboxed
 * frame. The frame is /s-frame.html, a static page with its own header policy (vercel.json: scripts
 * and styles inline, no network), loaded without same-origin access, so it cannot read this page or
 * call its API. The mockup's HTML is handed over by postMessage and written into that page: a
 * `srcdoc` frame would inherit this page's strict policy and its scripts would never run. The two
 * pages speak only to each other: each checks the window and the origin of what it hears.
 */

const MIN_HEIGHT = 160;
const MAX_HEIGHT = 2400;

export const DesignStill = ({ still }: { still: PlanStill }) => (
  <figure className="sh-frame">
    <figcaption className="sh-frame-bar">{still.title}</figcaption>
    <img src={still.image} alt={still.title} />
  </figure>
);

export function MockupFrame({ html, title }: { html: string; title: string }) {
  const frame = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(360);
  const [src] = useState(() => (typeof window === "undefined" ? "/s-frame.html" : `/s-frame.html#${encodeURIComponent(window.location.origin)}`));

  const hand = useCallback(() => {
    // The frame has an opaque origin, so "*" is the only address that reaches it; only it holds the window.
    frame.current?.contentWindow?.postMessage({ type: "qualitylayer:mockup", html: withCsp(html) }, "*");
  }, [html]);

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      // Only this frame's own window may speak, from its opaque origin, and only about itself.
      if (frame.current === null || event.source !== frame.current.contentWindow || event.origin !== "null") return;
      const data = event.data as { type?: unknown; height?: unknown } | null;
      if (data === null || typeof data !== "object") return;
      if (data.type === "qualitylayer:frame-ready") hand();
      else if (data.type === "qualitylayer:height" && typeof data.height === "number" && Number.isFinite(data.height))
        setHeight(Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, Math.round(data.height))));
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [hand]);

  return (
    <figure className="sh-frame" data-testid="shared-mockup">
      <figcaption className="sh-frame-bar">mockup · clickable</figcaption>
      <iframe
        // A new mockup is a new frame: the page writes into itself once.
        key={html}
        ref={frame}
        title={title}
        src={src}
        sandbox="allow-scripts"
        referrerPolicy="no-referrer"
        onLoad={hand}
        style={{ height }}
      />
    </figure>
  );
}

/** The place of a mockup the link does not carry: the page says so instead of showing a path. */
export const MissingMockup = () => (
  <p className="sh-frame-missing" data-testid="shared-mockup-missing">
    The mockup is not part of this link. Ask for a new link to see it.
  </p>
);
