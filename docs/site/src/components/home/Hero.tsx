import { Link } from "react-router-dom";
import { useDownload } from "@/hooks/useDownload";
import { DESCRIPTION } from "@/lib/product";

/** Opens on the offer and its working action: the visitor's own download, one click away. */
const Hero = () => {
  const download = useDownload();
  return (
    <section className="sx-hero" id="top" aria-labelledby="hero-h">
      <h1 id="hero-h" className="sx-h1">The <span>software factory</span> for your coding agents</h1>
      <p className="sx-lede">{DESCRIPTION}</p>
      <div className="sx-ctas">
        {download.direct ? <a className="sx-btn sx-btn-p" href={download.href}>{download.label}</a> : <Link className="sx-btn sx-btn-p" to={download.href}>{download.label}</Link>}
        <a className="sx-btn sx-btn-s" href="#tour">See how it works</a>
      </div>
      <p className="sx-meta">For one developer or a whole team · Claude Code and Codex · <Link to="/download">macOS, Windows and Linux</Link> · 7-day trial</p>
    </section>
  );
};

export default Hero;
