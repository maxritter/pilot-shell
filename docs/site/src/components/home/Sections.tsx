import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Questions from "@/components/Questions";
import { useDownload } from "@/hooks/useDownload";
import { FAQS } from "@/lib/content";
import { BRAND_LINE } from "@/lib/product";
import Intro from "./Intro";
import Editorial from "./Editorial";

function Install() {
  const download = useDownload();
  return (
    <section id="install" className="mx-sec" aria-labelledby="install-h">
      <div className="mx-wrap">
        <div className="mx-end">
          <div>
            <p className="mx-qbd"><span aria-hidden="true" className="w7-mark" />{BRAND_LINE}</p>
            <h2 id="install-h">Start with your next change</h2>
            <p>Open the App or browser. Choose Chat with Claude Code or Codex, or plan a Feature or Bugfix with Claude Code, Codex, Cursor, Grok, Antigravity, Pi or OpenCode. Your own terminal, VS Code and other IDEs work too. On your own or with your team, start with a 7-day trial.</p>
            <p className="mx-endn">On a server, in WSL or in a container? <Link to="/download">Install the command line</Link></p>
          </div>
          <div className="sx-ctas">
            <Button asChild size="xl">{download.direct ? <a href={download.href}>{download.label}</a> : <Link to={download.href}>{download.label}</Link>}</Button>
            <Button asChild variant="outline" size="xl"><Link to="/pricing">See pricing</Link></Button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Sections() {
  return (
    <>
      <Intro />
      <Editorial />
      <Questions faqs={FAQS} />
      <Install />
    </>
  );
}
