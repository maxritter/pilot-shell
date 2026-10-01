import { useNarrow } from "@/hooks/useNarrow";
import { DESCRIPTION } from "@/lib/product";

const Hero = () => {
  // Phones have no clickable Cockpit, so the second button walks through how it works instead.
  const narrow = useNarrow();
  return (
    <section className="w7-hero" id="top" aria-labelledby="hero-h">
      <div className="w7-hero-wrap">
        <h1 id="hero-h">The <span className="w7-accent">software factory</span> for your coding agents</h1>
        <div className="w7-hero-row">
          <p className="w7-hero-lead">{DESCRIPTION}</p>
          <div className="w7-btns">
            <a className="w7-btn-p" href="#install">Install QualityLayer</a>
            {narrow ? <a className="w7-btn-s" href="#lifecycle">How it works</a> : <a className="w7-btn-s" href="#cockpit">Try the Cockpit</a>}
          </div>
          {narrow ? <p className="w7-hero-hint">The clickable Cockpit demo runs on a laptop or tablet.</p> : null}
        </div>
      </div>
    </section>
  );
};

export default Hero;
