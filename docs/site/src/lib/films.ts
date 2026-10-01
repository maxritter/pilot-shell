/** The two YouTube films. Posters are local, so nothing loads from YouTube until a visitor plays one. */
export const FILMS = [
  {
    id: "FQuSwPxdNzk",
    name: "Overview",
    length: "3:20",
    about: "Why QualityLayer exists, and how you and your team plan, build and check a change with it.",
    poster: "/videos/launch.webp",
  },
  {
    id: "VL3WPkWolPc",
    name: "Walkthrough",
    length: "9:57",
    about: "The Cockpit step by step, on one hard change: usage-based billing across nine services.",
    poster: "/videos/walkthrough.webp",
  },
] as const;

export type Film = (typeof FILMS)[number];

/** The privacy-enhanced player: no YouTube cookies until the visitor plays the video. */
export const embedUrl = (id: string) => `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
