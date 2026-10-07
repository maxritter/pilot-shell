import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Questions from "@/components/Questions";
import { useDownload } from "@/hooks/useDownload";
import { FAQS } from "@/lib/content";
import Intro from "./Intro";
import Tour from "./Tour";

function Install() {
  const download = useDownload();
  return (
    <section id="install" className="mx-sec" aria-labelledby="install-h">
      <div className="mx-wrap">
        <div className="mx-end">
          <div>
            <span aria-hidden="true" className="sx-mark" />
            <h2 id="install-h">Start with your next change</h2>
            <p>The App sets up Claude Code and Codex on first start. Every plan starts with a 7-day trial.</p>
            <div className="sx-ctas">
              <Button asChild size="xl">{download.direct ? <a href={download.href}>{download.label}</a> : <Link to={download.href}>{download.label}</Link>}</Button>
              <Button asChild variant="outline" size="xl"><Link to="/pricing">See pricing</Link></Button>
            </div>
            <p className="mx-endn">On a server, in WSL or in a container? <Link to="/download">Install the command line</Link></p>
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
      <Tour />
      <Questions faqs={FAQS} />
      <Install />
    </>
  );
}
