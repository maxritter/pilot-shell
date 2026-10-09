// Written by docs/video/scripts/publish.mjs: the films on the media host (Cloudflare R2 behind the
// qualitylayer-media Worker). Re-run the publish script for a new cut instead of editing by hand.

export type Film = { src: string; poster: string; duration: number };

export const FILMS = {
  overview: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/overview.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/overview.webp",
    duration: 292,
  },
} satisfies Record<string, Film>;
