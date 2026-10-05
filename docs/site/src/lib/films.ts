// Written by video/scripts/publish.mjs: the films on the media host (Cloudflare R2 behind the
// qualitylayer-media Worker). Re-run the publish script for a new cut instead of editing by hand.

export type Film = { src: string; poster: string; duration: number };

export const FILMS = {
  launch: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/launch-v8.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/launch-v8.webp",
    duration: 252,
  },
  walkthrough: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v4.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v4.webp",
    duration: 609,
  },
} satisfies Record<string, Film>;
