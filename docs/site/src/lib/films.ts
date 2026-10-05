// Written by video/scripts/publish.mjs: the films on the media host (Cloudflare R2 behind the
// qualitylayer-media Worker). Re-run the publish script for a new cut instead of editing by hand.

export type Film = { src: string; poster: string; duration: number };

export const FILMS = {
  launch: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/launch-v7.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/launch-v7.webp",
    duration: 231,
  },
  walkthrough: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v3.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v3.webp",
    duration: 590,
  },
} satisfies Record<string, Film>;
