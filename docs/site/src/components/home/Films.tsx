import { useState } from "react";
import { FILMS, type Film } from "@/lib/films";

const CARDS: { id: keyof typeof FILMS; title: string }[] = [
  { id: "launch", title: "Overview" },
  { id: "walkthrough", title: "Every step, in the App" },
];

const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

/** Two films under the hero: a poster and a play button until clicked, then the video itself. */
const Films = () => {
  const [playing, setPlaying] = useState<string | null>(null);
  return (
    <section className="sx-films" id="films" aria-labelledby="films-h">
      <div className="sx-wrap">
        <h2 id="films-h" className="sr-only">Watch QualityLayer</h2>
        <div className="sx-fgrid">
          {CARDS.map(({ id, title }) => {
            const film: Film = FILMS[id];
            const length = clock(film.duration);
            return (
              <article key={id} className="sx-film">
                <div className="sx-fframe">
                  {playing === id ? (
                    // The films carry their words as on-screen subtitles.
                    <video className="sx-fvid" src={film.src} poster={film.poster} controls autoPlay playsInline preload="auto" />
                  ) : (
                    <button type="button" className="sx-fposter" onClick={() => setPlaying(id)} aria-label={`Play ${title}, ${length}`}>
                      <img className="sx-fimg" src={film.poster} alt="" width={1920} height={1080} decoding="async" />
                      <span className="sx-fplay" aria-hidden="true">
                        <svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">
                          <path d="M8 5.5v13a1 1 0 0 0 1.53.85l10.4-6.5a1 1 0 0 0 0-1.7L9.53 4.65A1 1 0 0 0 8 5.5z" />
                        </svg>
                      </span>
                    </button>
                  )}
                </div>
                <p className="sx-ftitle">
                  {title} <span>{length}</span>
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Films;
