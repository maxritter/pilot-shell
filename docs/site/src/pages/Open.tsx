import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router-dom";
import { useCopy } from "@/hooks/useCopy";
import { useNarrow } from "@/hooks/useNarrow";
import { isPhone } from "@/lib/device";
import { type OpenLinks, openLinks } from "@/lib/open-link";
import "@/styles/app-pages.css";

/**
 * Where a Slack DM lands. It tries the reader's QualityLayer App, then offers the three ways on.
 * It only reads its own address: no request, no analytics, and no key, which nothing in a DM carries.
 */

/** How long the App gets to open before the three buttons show. */
const ATTEMPT_MS = 1500;
/** A window this narrow gets the phone page, whatever the device. */
const PHONE_WIDTH = 600;

type Device = "computer" | "phone";
type Phase = "trying" | "offer";

const what = (links: OpenLinks) => (links.path.startsWith("ask/") ? "ask" : "task");

function CopyLink() {
  const { copy, state } = useCopy(typeof window === "undefined" ? "" : window.location.href);
  return (
    <button type="button" className="w7-btn-p" onClick={() => void copy()}>
      {state === "done" ? "Copied" : state === "error" ? "Select the address and copy it" : "Copy the link"}
    </button>
  );
}

/** The page for a valid link; on a computer its hidden frame asks the browser to hand the link to the App. */
export function OpenView({ links, device, phase }: { links: OpenLinks; device: Device; phase: Phase }) {
  if (device === "phone") {
    return (
      <>
        <h1>Open this on your computer</h1>
        <p>Asks are answered in the QualityLayer App on your computer, or by your own agent there.</p>
        <div className="ap-stack">
          <CopyLink />
        </div>
      </>
    );
  }
  return (
    <>
      <h1>{`Opening the ${what(links)} in the QualityLayer App…`}</h1>
      <p>If nothing happens, the App may not be installed on this computer.</p>
      {phase === "offer" && (
        <div className="ap-stack">
          <a className="w7-btn-p" href={links.app}>Open in the App</a>
          <a className="w7-btn-s" href={links.browser}>Open in this browser</a>
          <a className="w7-btn-s" href="/download">Get the QualityLayer App</a>
        </div>
      )}
      <p className="ap-fine">{`This page only reads the link. Nothing about the ${what(links)}, and no access key, is sent to qualitylayer.dev.`}</p>
      <iframe hidden title="" src={links.app} />
    </>
  );
}

const Open = () => {
  const { pathname } = useLocation();
  const links = openLinks(pathname);
  const narrow = useNarrow(PHONE_WIDTH);
  const device: Device = narrow || isPhone(typeof navigator === "undefined" ? "" : navigator.userAgent) ? "phone" : "computer";
  const [phase, setPhase] = useState<Phase>("trying");
  const trying = links !== null && device === "computer";

  useEffect(() => {
    if (!trying) return;
    const timer = setTimeout(() => setPhase("offer"), ATTEMPT_MS);
    return () => clearTimeout(timer);
  }, [trying]);

  return (
    <div className="w7-root ap-page">
      <Helmet>
        <title>Open in the QualityLayer App</title>
        <meta name="robots" content="noindex" />
      </Helmet>
      <main id="main" className="ap-center">
        <span className="w7-mark ap-mark" aria-hidden="true" />
        {links === null ? (
          <>
            <h1>This link is not valid</h1>
            <p>Open the ask or the task from the message again, or from the QualityLayer App.</p>
          </>
        ) : (
          <OpenView links={links} device={device} phase={phase} />
        )}
      </main>
    </div>
  );
};

export default Open;
