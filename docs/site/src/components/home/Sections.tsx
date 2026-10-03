import { Link } from "react-router-dom";
import Questions from "@/components/Questions";
import { useCopy } from "@/hooks/useCopy";
import { useDownload } from "@/hooks/useDownload";
import { FAQS } from "@/lib/content";
import { INSTALL_COMMAND } from "@/lib/product";
import Tour from "./Tour";

function Install() {
  const { copy, state, status } = useCopy(INSTALL_COMMAND);
  const download = useDownload();
  return (
    <section id="install" className="sx-end" aria-labelledby="install-h">
      <span aria-hidden="true" className="sx-mark" />
      <h2 id="install-h" className="sx-h2" style={{ margin: "24px auto 0", maxWidth: "21ch" }}>Start with your next change. Bring your team when it’s ready.</h2>
      <p className="sx-lede" style={{ marginTop: 16 }}>The App sets up QualityLayer for Claude Code and Codex on first start, no terminal needed.</p>
      <div className="sx-dls">
        {download.direct ? <a className="sx-btn sx-btn-p" href={download.href}>{download.label}</a> : <Link className="sx-btn sx-btn-p" to={download.href}>{download.label}</Link>}
        <Link className="sx-btn sx-btn-s" to="/download">All downloads</Link>
      </div>
      <p className="sx-cmdn">On a server, in WSL or in a container, install the command line. The App then opens in your browser.</p>
      <div className="sx-cmd">
        <code>{INSTALL_COMMAND}</code>
        <button type="button" onClick={() => void copy()} aria-label="Copy install command">
          {state === "done" ? "Copied" : state === "error" ? "Select the text" : "Copy"}
        </button>
      </div>
      <p className="w7-sr" role="status">{status}</p>
      <p className="sx-small">macOS, Windows and Linux · 7-day trial · <Link to="/pricing">See pricing</Link></p>
    </section>
  );
}

export default function Sections() {
  return (
    <>
      <Tour />
      <Questions faqs={FAQS} />
      <Install />
    </>
  );
}
