import { useState } from "react";
import { embedUrl, type Film as FilmData, FILMS } from "@/lib/films";

function Film({ film }: { film: FilmData }) {
  const [playing, setPlaying] = useState(false);
  const title = `QualityLayer ${film.name.toLowerCase()} video, ${film.length}`;
  return (
    <figure className="w7-film">
      <div className="w7-film-frame">
        {playing ? (
          <iframe
            src={embedUrl(film.id)}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
          />
        ) : (
          <button type="button" className="w7-film-play" onClick={() => setPlaying(true)} aria-label={`Play the ${title}`}>
            <img src={film.poster} alt="" width={1280} height={720} loading="lazy" decoding="async" />
            <span className="w7-film-icon" aria-hidden="true" />
          </button>
        )}
      </div>
      <figcaption>
        <span className="w7-film-name">
          {film.name} <span className="w7-film-len">{film.length}</span>
        </span>
        <span className="w7-film-about">{film.about}</span>
      </figcaption>
    </figure>
  );
}

export default function Films() {
  return (
    <section id="videos" className="w7-sec w7-films" aria-labelledby="videos-h">
      <div className="w7-wrap">
        <h2 id="videos-h" className="w7-h2">
          Watch the overview, then the walkthrough
        </h2>
        <p className="w7-lead">Two short videos with the real Cockpit. The player loads from YouTube only when you press play.</p>
        <div className="w7-films-grid">
          {FILMS.map((film) => (
            <Film key={film.id} film={film} />
          ))}
        </div>
      </div>
    </section>
  );
}
