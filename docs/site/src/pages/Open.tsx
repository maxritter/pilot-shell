import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router-dom";
import { useCopy } from "@/hooks/useCopy";
import { useNarrow } from "@/hooks/useNarrow";
import { isPhone } from "@/lib/device";
import { type AttemptPhase, startAttempt } from "@/lib/open-attempt";
import { type OpenLinks, openLinks } from "@/lib/open-link";
import "@/styles/app-pages.css";

/**
 * Where a Slack message lands. It tries the reader's QualityLayer App, then offers the three ways on.
 * It only reads its own address: no request, no analytics, and no key, which nothing in a message carries.
 */

/** How long the App gets to open before the three ways on show. */
const ATTEMPT_MS = 1500;
/** A window this narrow gets the phone page, whatever the device. */
const PHONE_WIDTH = 600;

type Device = "computer" | "phone";
type Phase = "trying" | AttemptPhase;

/** What the link points at, in the App's words: a question, or a task. */
const what = (links: OpenLinks) => (links.path.startsWith("ask/") ? "question" : "task");

function CopyLink() {
  const { copy, state } = useCopy(typeof window === "undefined" ? "" : window.location.href);
  return (
    <button type="button" className="w7-btn-s" onClick={() => void copy()}>
      {state === "done" ? "Copied" : state === "error" ? "Select the address and copy it" : "Copy the link"}
    </button>
  );
}

/** The page for a valid link; on a computer its hidden frame asks the browser to hand the link to the App. */
export function OpenView({ links, device, phase, onOptions }: { links: OpenLinks; device: Device; phase: Phase; onOptions?: () => void }) {
  if (device === "phone") {
    return (
      <>
        <h1>Open this on your computer</h1>
        <p>{`${links.path.startsWith("ask/") ? "Questions are answered in" : "Tasks open in"} the QualityLayer App, where the Plan and your agent are.`}</p>
        <div className="ap-row">
          <CopyLink />
        </div>
      </>
    );
  }
  return (
    <>
      <h1>{phase === "opened" ? "Opened in the QualityLayer App" : `Opening the ${what(links)} in the QualityLayer App…`}</h1>
      <div aria-live="polite">
        {phase === "opened" && (
          <p>
            You can close this tab.{" "}
            <button type="button" className="ap-link" onClick={onOptions}>
              Nothing opened?
            </button>
          </p>
        )}
        {phase === "offer" && (
          <>
            <p>Nothing happened? Pick one:</p>
            <div className="ap-row">
              <a className="w7-btn-p" href={links.app}>Open in the App</a>
              <a className="w7-btn-s" href={links.browser}>Open in this browser</a>
            </div>
            <a className="ap-link" href="/download">Get the QualityLayer App</a>
          </>
        )}
      </div>
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
    return startAttempt({ win: window, doc: document, ms: ATTEMPT_MS, onPhase: setPhase });
  }, [trying]);

  return (
    <div className="w7-root ap-page">
      <Helmet>
        <title>Open in the QualityLayer App</title>
        <meta name="robots" content="noindex" />
      </Helmet>
      <main id="main" className="ap-center ap-open">
        <span className="w7-mark ap-mark" aria-hidden="true" />
        {links === null ? (
          <>
            <h1>This link is not valid</h1>
            <p>Open the question or the task from the message again, or from the QualityLayer App.</p>
          </>
        ) : (
          <OpenView links={links} device={device} phase={phase} onOptions={() => setPhase("offer")} />
        )}
      </main>
    </div>
  );
};

export default Open;
