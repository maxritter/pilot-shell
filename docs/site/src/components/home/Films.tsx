import { useState } from "react";
import { FILMS } from "@/lib/films";

const TITLE = "How QualityLayer works";

const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

/** The film under the hero: a poster and a play button until clicked, then the video itself. */
const Films = () => {
  const [playing, setPlaying] = useState(false);
  const film = FILMS.overview;
  const length = clock(film.duration);
  return (
    <section className="sx-films" id="films" aria-labelledby="films-h">
      <div className="sx-wrap">
        <h2 id="films-h" className="sr-only">Watch QualityLayer</h2>
        <article className="sx-film">
          <div className="sx-fframe">
            {playing ? (
              // The film shows its narration as captions, and chapter titles beside the App.
              <video className="sx-fvid" src={film.src} poster={film.poster} controls autoPlay playsInline preload="auto" />
            ) : (
              <button type="button" className="sx-fposter" onClick={() => setPlaying(true)} aria-label={`Play ${TITLE}, ${length}`}>
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
            {TITLE} <span>{length}</span>
          </p>
        </article>
      </div>
    </section>
  );
};

export default Films;
