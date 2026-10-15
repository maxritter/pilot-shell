import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useDownload } from "@/hooks/useDownload";
import { FILMS } from "@/lib/films";
import { DESCRIPTION } from "@/lib/product";

const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const EXAMPLE = "/ql add usage-based billing";

function ExamplePrompt() {
  const root = useRef<HTMLDivElement>(null);
  const typed = useRef<HTMLElement>(null);
  const [replay, setReplay] = useState(0);
  const [canReplay, setCanReplay] = useState(false);
  useEffect(() => {
    const element = root.current;
    const text = typed.current;
    if (!element || !text) return;
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    let index = 0;
    let timer = 0;
    const rect = element.getBoundingClientRect();
    let visible = rect.bottom >= 0 && rect.top < window.innerHeight;
    const cancel = () => { window.clearTimeout(timer); timer = 0; };
    const schedule = () => {
      if (timer || document.hidden || !visible || media.matches || index >= EXAMPLE.length) return;
      timer = window.setTimeout(() => {
        timer = 0;
        text.textContent = EXAMPLE.slice(0, ++index);
        schedule();
      }, 45);
    };
    const sync = () => {
      cancel();
      setCanReplay(!media.matches);
      if (media.matches) { index = EXAMPLE.length; text.textContent = EXAMPLE; }
      else schedule();
    };
    text.textContent = media.matches ? EXAMPLE : "";
    const observer = typeof IntersectionObserver === "undefined" ? null : new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) schedule(); else cancel();
    });
    observer?.observe(element);
    media.addEventListener("change", sync);
    document.addEventListener("visibilitychange", sync);
    sync();
    return () => {
      cancel(); observer?.disconnect();
      media.removeEventListener("change", sync);
      document.removeEventListener("visibilitychange", sync);
    };
  }, [replay]);
  return (
    <div className="sx-prompt" ref={root}>
      <code><span className="sx-prompt-source">{EXAMPLE}</span><span ref={typed} className="sx-prompt-typed" aria-hidden="true">{EXAMPLE}</span></code>
      <button type="button" aria-hidden={!canReplay} disabled={!canReplay} tabIndex={canReplay ? 0 : -1} style={{ visibility: canReplay ? "visible" : "hidden" }} onClick={() => setReplay(value => value + 1)}>Replay prompt</button>
      <p>Illustrative prompt; no task is submitted.</p>
    </div>
  );
}

/** The film, opened over the page from the hero. Escape or Close puts focus back on the button that opened it. */
function FilmDialog({ onClose }: { onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const close = useRef<HTMLButtonElement>(null);
  const film = FILMS.overview;
  useEffect(() => {
    const dialog = ref.current;
    if (dialog && !dialog.open) dialog.showModal();
    // showModal focuses the first control, the video, whose focus ring framed the film; Close takes focus instead.
    close.current?.focus();
  }, []);
  return (
    <dialog ref={ref} className="mx-filmov" aria-label={`How QualityLayer works, ${clock(film.duration)}`} onClose={onClose} onClick={(e) => { if (e.target === e.currentTarget) ref.current?.close(); }}>
      <div className="mx-filmbox">
        {/* The film shows its narration as captions, and chapter titles beside the App. */}
        <video src={film.src} poster={film.poster} controls autoPlay playsInline preload="auto" />
      </div>
      <Button type="button" variant="outline" size="xl" ref={close} className="mx-filmx" onClick={() => ref.current?.close()}>Close</Button>
    </dialog>
  );
}

/** Opens on the offer and its working action: the visitor's own download, one click away, and the film. */
const Hero = () => {
  const download = useDownload();
  const [film, setFilm] = useState(false);
  const opener = useRef<HTMLButtonElement>(null);
  return (
    <section className="sx-hero" id="top" aria-labelledby="hero-h">
      <span aria-hidden="true" className="sx-mark mx-hmark" />
      <h1 id="hero-h" className="sx-h1">The <span className="mx-acc">software factory</span> for your coding agents</h1>
      <p className="sx-lede">{DESCRIPTION}</p>
      <ExamplePrompt />
      <div className="sx-ctas">
        <Button asChild size="xl">{download.direct ? <a href={download.href}>{download.label}</a> : <Link to={download.href}>{download.label}</Link>}</Button>
        <Button ref={opener} type="button" variant="outline" size="xl" onClick={() => setFilm(true)}>
          <svg className="mx-play" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M8 5.5v13a1 1 0 0 0 1.53.85l10.4-6.5a1 1 0 0 0 0-1.7L9.53 4.65A1 1 0 0 0 8 5.5z" /></svg>
          Watch the film <span className="mx-dur">{clock(FILMS.overview.duration)}</span>
        </Button>
      </div>
      <p className="sx-meta">For one developer or a whole team · <Link to="/download">macOS, Windows and Linux</Link> · 7-day trial</p>
      {film ? <FilmDialog onClose={() => { setFilm(false); opener.current?.focus(); }} /> : null}
    </section>
  );
};

export default Hero;
